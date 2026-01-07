import secrets
import json
def generate_api_keys():
        # Generate Browser Extension API Key
  browser_extension_key = secrets.token_urlsafe(32)
  
         # Generate Content Discovery API Key
  content_discovery_key = secrets.token_urlsafe(32)
   
  print("Generated API Keys:")
  print(f"Browser Extension API Key: {browser_extension_key}")
  print(f"Content Discovery API Key: {content_discovery_key}")
   
        # Create a config snippet to add to your config.json
  config_snippet = {
    "browser_extension_api_key": browser_extension_key,
    "content_discovery_api_key": content_discovery_key
  }
   
  print("\nAdd these to your config.json:")
  print(json.dumps(config_snippet, indent=2))
   
  return browser_extension_key, content_discovery_key
   
if __name__ == "__main__":
  browser_key, content_key = generate_api_keys()