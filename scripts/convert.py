import argparse
import os
import torch
from safetensors.torch import load_file
import json
from typing import Dict, Any
import struct
from concurrent.futures import ThreadPoolExecutor
import numpy as np

def convert_tensor_to_numpy(tensor: torch.Tensor) -> np.ndarray:
    """Convert tensor to numpy array, handling special data types."""
    if tensor.dtype == torch.bfloat16:
        # Convert bfloat16 to float32 first
        return tensor.to(torch.float32).cpu().numpy()
    elif tensor.dtype == torch.float16:
        # Convert float16 to float32
        return tensor.to(torch.float32).cpu().numpy()
    else:
        return tensor.cpu().numpy()

def load_safetensor_file(filepath: str) -> Dict[str, torch.Tensor]:
    """Load a safetensors file."""
    print(f"Loading {filepath}...")
    return load_file(filepath)

def combine_safetensors(input_dir: str) -> Dict[str, torch.Tensor]:
    """Combine multiple safetensors files using parallel loading."""
    model_files = sorted([
        f for f in os.listdir(input_dir) 
        if f.startswith("model-") and f.endswith(".safetensors")
    ])
    
    if not model_files:
        raise FileNotFoundError(f"No safetensors files found in {input_dir}")
    
    print(f"Found model files: {model_files}")
    
    # Load files in parallel using ThreadPoolExecutor
    combined_state_dict = {}
    with ThreadPoolExecutor(max_workers=len(model_files)) as executor:
        future_to_file = {
            executor.submit(load_safetensor_file, os.path.join(input_dir, filename)): filename
            for filename in model_files
        }
        
        for future in future_to_file:
            state_dict = future.result()
            combined_state_dict.update(state_dict)
    
    return combined_state_dict

def write_gguf_metadata(f, config: Dict[str, Any]):
    """Write GGUF metadata efficiently."""
    f.write(struct.pack('<Q', len(config)))
    encoded_items = [(key.encode('utf-8'), value) for key, value in config.items()]
    
    for key_bytes, value in encoded_items:
        f.write(struct.pack('<Q', len(key_bytes)))
        f.write(key_bytes)
        
        if isinstance(value, str):
            value_bytes = value.encode('utf-8')
            f.write(struct.pack('<I', 1))
            f.write(struct.pack('<Q', len(value_bytes)))
            f.write(value_bytes)
        elif isinstance(value, int):
            f.write(struct.pack('<I', 2))
            f.write(struct.pack('<q', value))
        elif isinstance(value, float):
            f.write(struct.pack('<I', 3))
            f.write(struct.pack('<d', value))
        elif isinstance(value, bool):
            f.write(struct.pack('<I', 4))
            f.write(struct.pack('<?', value))

def convert_to_gguf(state_dict: Dict[str, torch.Tensor], output_path: str, config: Dict[str, Any]):
    """Convert state dict to GGUF format with optimized writing."""
    print("Converting to GGUF format...")
    
    temp_path = output_path + ".temp"
    
    with open(temp_path, 'wb', buffering=1024*1024) as f:
        f.write(b"GGUF")
        f.write(struct.pack('<I', 1))
        
        # Write tensor count
        f.write(struct.pack('<Q', len(state_dict)))
        
        # Write metadata
        write_gguf_metadata(f, config)
        
        # Write tensor data efficiently
        total_tensors = len(state_dict)
        for i, (key, tensor) in enumerate(state_dict.items(), 1):
            print(f"Processing tensor {i}/{total_tensors}: {key} (dtype: {tensor.dtype})")
            try:
                data = convert_tensor_to_numpy(tensor)
                f.write(data.tobytes())
            except Exception as e:
                print(f"Error processing tensor {key}: {str(e)}")
                raise
    
    os.replace(temp_path, output_path)
    print("Conversion completed successfully!")

def main():
    parser = argparse.ArgumentParser(description="Convert Llama model to GGUF format")
    parser.add_argument("--input", type=str, required=True, help="Input directory containing safetensors files")
    parser.add_argument("--output", type=str, required=True, help="Output GGUF file path")
    parser.add_argument("--config", type=str, help="Optional JSON config file")
    parser.add_argument("--batch-size", type=int, default=1024*1024, help="Batch size for tensor processing")
    
    args = parser.parse_args()
    
    # Set PyTorch to use multiple threads
    torch.set_num_threads(os.cpu_count())
    print(f"Using {os.cpu_count()} CPU threads")
    
    # Load or create config
    config = {
        "model_type": "llama",
        "context_length": 4096,
        "vocab_size": 32000,
        "hidden_size": 4096,
        "num_attention_heads": 32,
        "num_hidden_layers": 32
    }
    
    if args.config:
        with open(args.config) as f:
            config.update(json.load(f))
    
    print(f"Starting conversion from {args.input} to {args.output}")
    
    # Load and combine model parts
    state_dict = combine_safetensors(args.input)
    
    # Convert to GGUF
    convert_to_gguf(state_dict, args.output, config)
    
    print(f"Conversion complete! Model saved to {args.output}")

if __name__ == "__main__":
    main()