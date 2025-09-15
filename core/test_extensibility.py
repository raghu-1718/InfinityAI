from core.extensibility import run_all_plugins

if __name__ == "__main__":
    plugin_folder = "c:/Users/Raghu/.docker/InfinityAI/core/extensibility_plugins"
    results = run_all_plugins(plugin_folder)
    print("Plugin execution results:", results)
