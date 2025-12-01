"""Script used to populate .env.sample from .env, for documentation purposes."""

def get_env_variable_names(env_path=".env"):
    """Returns a list of all environment variable names in the .env file."""
    names = []
    with open(env_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                name = line.split("=", 1)[0].strip()
                names.append(name)
    return names

def env_sample_check(env_path=".env", sample_path=".env.sample"):
    """Returns a list of variable names present in .env but missing from .env.sample."""
    env_names = set(get_env_variable_names(env_path))
    sample_names = set(get_env_variable_names(sample_path))
    missing = list(env_names - sample_names)
    return missing


if __name__ == "__main__":
    missing_vars = env_sample_check()
    if missing_vars:
        print("The following environment variables are missing from .env.sample:")
        for var in missing_vars:
            print(f"- {var}")
    else:
        print("All environment variables in .env are present in .env.sample.")