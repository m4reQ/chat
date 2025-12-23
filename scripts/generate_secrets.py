import secrets

if __name__ == '__main__':
    print('Generating secrets...')

    lines = (
        f'JWT_SECRET={secrets.token_hex(32)}',
        f'EMAIL_VERIFICATION_KEY={secrets.token_hex(32)}',
        f'EMAIL_VERIFICATION_SALT={secrets.token_hex(32)}')

    with open('.env', 'w+') as env_file:
        env_file.writelines(lines)
    
    
