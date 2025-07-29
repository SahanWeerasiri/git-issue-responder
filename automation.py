import sys
import os
import subprocess
from typing import List
import dotenv
from ai_agent import llm_request  # Assuming this is in a separate file

# Configure environment variables
dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Global variables for issue information
title = ""
description = ""

class FileInfo:
    """Class to hold information about a file in the project."""
    def __init__(self, path: str, name: str, content: str = "", summary: str = ""):
        self.path = path
        self.name = name
        self.content = content
        self.summary = summary

    def __repr__(self):
        return f"FileInfo(path={self.path}, name={self.name}, summary={self.summary[:50]}...)"

def read_file_structure(root_dir: str = ".") -> List[FileInfo]:
    """
    Reads the file structure and returns a list of files with paths, names, and summaries.
    
    Args:
        root_dir: The root directory to start scanning from (defaults to current directory)
    
    Returns:
        List of FileInfo objects containing file information
    """
    file_list = []
    
    for root, _, files in os.walk(root_dir):
        # Skip hidden directories (like .git)
        if os.path.basename(root).startswith('.'):
            continue
            
        for file in files:
            # Skip hidden files
            if file.startswith('.'):
                continue
                
            file_path = os.path.join(root, file)
            if "project/" not in file_path:
                continue
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    summary = generate_file_summary(content)
                    file_list.append(FileInfo(path=file_path, name=file, content=content, summary=summary))
            except (UnicodeDecodeError, PermissionError, IOError) as e:
                # Skip binary files or files we can't read
                continue
                
    return file_list

def generate_file_summary(content: str) -> str:
    """
    Generates a summary of the file content using Gemini API.
    
    Args:
        content: The content of the file to summarize
        
    Returns:
        A summary of the file content
    """
    prompt = f"""
    Please provide a concise summary of the following code file content.
    Focus on the main purpose, key functions, and important classes.
    Keep the summary under 100 words.
    
    File content:
    {content}
    """
    
    try:
        request = llm_request(prompt)
        summary = request.get_llm_response()
        return summary
    except Exception as e:
        print(f"Failed to generate summary: {str(e)}")
        return "Summary unavailable"

def gemini_support_for_find_the_correct_file(file_list: List[FileInfo], issue_title: str, issue_description: str) -> List[FileInfo]:
    """
    Finds the correct files to be updated based on the issue and description.
    
    Args:
        file_list: List of FileInfo objects representing the project files
        issue_title: Title of the GitHub issue
        issue_description: Description of the GitHub issue
        
    Returns:
        List of FileInfo objects that likely need modification
    """
    prompt = f"""
    Based on the following issue:
    Title: {issue_title}
    Description: {issue_description}
    
    And these project files with their summaries:
    {[f"{f.path}: {f.summary}" for f in file_list]}
    
    Please identify which files likely need to be modified to address this issue.
    Return only the full paths of the relevant files, one per line.
    """
    
    try:
        request = llm_request(prompt)
        response = request.get_llm_response()
        
        # Parse the response to get file paths
        relevant_paths = [path.strip() for path in response.split('\n') if path.strip()]
        
        # Filter the file list to only include relevant files
        relevant_files = [f for f in file_list if f.path in relevant_paths]
        
        return relevant_files
    except Exception as e:
        print(f"Failed to identify relevant files: {str(e)}")
        return []

def update_files(files_to_update: List[FileInfo], issue_title: str, issue_description: str) -> None:
    """
    Updates the selected files to reflect the changes based on the issue and description.
    
    Args:
        files_to_update: List of FileInfo objects to be updated
        issue_title: Title of the GitHub issue
        issue_description: Description of the GitHub issue
    """
    for file_info in files_to_update:
        try:
            updated_content = generate_updated_content(file_info.content, issue_title, issue_description)
            
            with open(file_info.path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
            print(f"Updated file: {file_info.path}")
        except Exception as e:
            print(f"Failed to update file {file_info.path}: {str(e)}")

def generate_updated_content(current_content: str, issue_title: str, issue_description: str) -> str:
    """
    Generates updated file content using Gemini API.
    
    Args:
        current_content: The current content of the file
        issue_title: Title of the GitHub issue
        issue_description: Description of the GitHub issue
        
    Returns:
        The updated content for the file
    """
    prompt = f"""
    Current file content:
    {current_content}
    
    Please update this file based on the following issue:
    Title: {issue_title}
    Description: {issue_description}
    
    Important guidelines:
    1. Preserve all existing functionality that isn't related to the issue
    2. Only make changes necessary to address the issue
    3. Maintain the existing code style and formatting
    4. Include comments explaining significant changes
    
    Return only the updated file content.
    """
    
    try:
        request = llm_request(prompt)
        return request.get_llm_response()
    except Exception as e:
        print(f"Failed to generate updated content: {str(e)}")
        return current_content

def git_commit(commit_message: str) -> bool:
    """
    Commits the changes to the git repository.
    
    Args:
        commit_message: The commit message to use
        
    Returns:
        True if commit was successful, False otherwise
    """
    try:
        subprocess.run(['git', 'add', '.'], check=True)
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git commit failed: {str(e)}")
        return False

def git_push() -> bool:
    """
    Pushes the committed changes to the remote repository.
    
    Returns:
        True if push was successful, False otherwise
    """
    try:
        subprocess.run(['git', 'push'], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Git push failed: {str(e)}")
        return False

def main():
    global title, description
    
    # Parse command line arguments
    args = sys.argv[1:]
    if len(args) < 2:
        print("Usage: python automation.py <title> <description>")
        sys.exit(1)
        
    title = args[0]
    description = args[1]
    
    print(f"Processing issue: {title}")
    print(f"Description: {description}\n")
    
    # Step 1: Read the file structure
    print("Scanning project files...")
    file_list = read_file_structure()
    print(f"Found {len(file_list)} files in the project.\n")
    
    # Step 2: Determine which files need to be updated
    print("Identifying files that need modification...")
    files_to_update = gemini_support_for_find_the_correct_file(file_list, title, description)
    print(f"Identified {len(files_to_update)} files that need updates:\n")
    for file in files_to_update:
        print(f"- {file.path}")
    print()
    
    # Step 3: Update the files
    print("Updating files...")
    update_files(files_to_update, title, description)
    print("File updates completed.\n")
    
    # Step 4: Commit changes
    commit_message = f"Fix: {title}\n\n{description}"
    print(f"Committing changes with message: {commit_message}")
    if git_commit(commit_message):
        print("Commit successful.")
    else:
        print("Commit failed. Exiting.")
        sys.exit(1)
    
    # Step 5: Push changes
    print("Pushing changes to remote repository...")
    if git_push():
        print("Push successful.")
    else:
        print("Push failed. Exiting.")
        sys.exit(1)
    
    print("\nAutomation completed successfully!")

if __name__ == "__main__":
    main()