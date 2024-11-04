export default {
    apps: [
        {
            name: 'ruby',
            script: 'pnpm',
            args: 'run start:ruby',
            watch: false,
            restart_delay: 3000,
            max_restarts: 10,
            env: {
                NODE_ENV: 'production'
            }
        },
        {
            name: 'degen',
            script: 'pnpm',
            args: 'run start:degen',
            watch: false,
            restart_delay: 3000,
            max_restarts: 10,
            env: {
                NODE_ENV: 'production'
            }
        },
        {
            name: 'trump',
            script: 'pnpm',
            args: 'run start:trump',
            watch: false,
            restart_delay: 3000,
            max_restarts: 10,
            env: {
                NODE_ENV: 'production'
            }
        },
        {
            name: 'tate',
            script: 'pnpm',
            args: 'run start:tate',
            watch: false,
            restart_delay: 3000,
            max_restarts: 10,
            env: {
                NODE_ENV: 'production'
            }
        },
        {
            name: 'all',
            script: 'pnpm',
            args: 'run start:all',
            watch: false,
            restart_delay: 3000,
            max_restarts: 10,
            env: {
                NODE_ENV: 'production'
            }
        }
    ]
};