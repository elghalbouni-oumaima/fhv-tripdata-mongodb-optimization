import kagglehub

# Download latest version
path = kagglehub.dataset_download("mxruedag/tlc-nyc-taxi-zones")

print("Path to dataset files:", path)