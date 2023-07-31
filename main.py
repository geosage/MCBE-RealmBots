import os
import subprocess
import asyncio

async def start_script(name):
    sub_directory = name

    current_script_path = os.path.abspath(__file__)
    parent_directory = os.path.dirname(current_script_path)
    sub_directory_path = os.path.join(parent_directory, sub_directory)

    os.chdir(sub_directory_path)

    try:
        subprocess.run(['python', 'main.py'], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
    else:
        print(f"{name} finished successfully!")

async def main():
    scripts_to_run = ['Neapolis-Bot']  # List of script names to execute

    # Create tasks for each script using asyncio.create_task()
    tasks = [start_script(name) for name in scripts_to_run]
    print("hello")

    # Wait for all tasks to complete using asyncio.gather()
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    # Run the main coroutine using asyncio.run()
    asyncio.run(main())
