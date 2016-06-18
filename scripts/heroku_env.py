from subprocess import call


def copy_env_to_heroku():
    with open('.env', 'r') as f:
        x = []
        for line in f.readlines():
            line = line[:-1]
            if line:
                x.append(line.replace('export ', ''))

        call(["heroku", "config:add"] + x)


copy_env_to_heroku()
