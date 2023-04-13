
import argparse
import os
import sys
# import subprocess
import ast
import requests
# import datetime
import json
import github
# conditional comment if not required
# import facebook

from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.editor import concatenate_videoclips


# Parse command-line arguments
parser = argparse.ArgumentParser(description="Download and concatenate videos from URL links.")
parser.add_argument("--urls", type=str, default=None, help="video URL links as '[]' list string")
parser.add_argument("--intro", type=str, default=None, help="Path to intro video file directory")
parser.add_argument("--outro", type=str, default=None, help="Path to outro video file directory")
parser.add_argument("--output", type=str, default="output.mp4", help="Name of the output file")
parser.add_argument("--tokenjson", type=str, default=None, help="Full token Json file as String")
parser.add_argument("--clientjson", type=str, default=None, help="Full client Json file as String")
parser.add_argument("--scopes", type=str, default=None, help="Full client Json file as String") # or add them as org secr or default
parser.add_argument("--gh_token", type=str, default=None, help="Your Github Token <Prefer Classic>") # or add them as org secr or default
# owner + repo
parser.add_argument("--owner_repo", type=str, default=None, help="Your Github Username + Repository Name") 
# tag
parser.add_argument("--tag", type=str, default=None, help="Your Github Artifacts release TAG") 



args = parser.parse_args()

client_secrets_file = "client_secret.json"
tokenjson = "token.json"


# # save Scopes
str_scope_list = args.scopes
scopes = ast.literal_eval(str_scope_list)


with open(tokenjson, 'w') as f:
    json.dump(json.loads(args.tokenjson), f)

token_file = os.path.join(os.getcwd(), tokenjson)
# path in env  saved 
token_file_path = os.path.abspath(token_file)


with open(client_secrets_file, 'w') as f:
    json.dump(json.loads(args.clientjson), f)
client_secrets_file_file = os.path.join(os.getcwd(), client_secrets_file)
# path in env  saved 
client_secrets_file_path = os.path.abspath(client_secrets_file_file)


# Download and validate the videos
video_clips = []
for url in ast.literal_eval(args.urls):
    r = requests.get(url)
    if r.status_code == 200:
        content_type = r.headers.get("content-type")
        if "video" in content_type:
            # save the video file to disk
            filename = os.path.basename(url)
            with open(filename, "wb") as f:
                f.write(r.content)

            # validate that the file is a video
            try:
                video_clip = VideoFileClip(filename)
                video_clips.append(video_clip)
            except Exception as e:
                print(f"[WARN] {filename} is not a valid video file")

        else:
            print(f"[WARN] {url} does not appear to be a video file")
    else:
        print(f"[ERROR] Failed to download {url}")

# Prepare the video clips
if args.intro is not None:
    intro_clip = VideoFileClip(args.intro)
    video_clips.insert(0, intro_clip)


if args.outro is not None:
    outro_clip = VideoFileClip(args.outro)
    video_clips.append(outro_clip)

# Concatenate the video clips
concatenated_clip = concatenate_videoclips(video_clips)

# Write the output file
output_file = os.path.join(os.getcwd(), args.output)
concatenated_clip.write_videofile(output_file)

# path in env  saved 
output_path = os.path.abspath(output_file)



# /////////////////////
# Authenticate with a personal access token
g = Github(args.gh_token)
# Get the repository object
# try:
repo = g.get_repo(args.owner_repo) #  todo change
# except GithubException:
#         print("Authentication Error. Try saving a GitHub Token in your Repo Secrets or Use the GitHub Actions Token, which is automatically used by the action.")
#         sys.exit(1)



# Get the release object
release = repo.get_release(args.tag) #  todo change


# Upload an artifact to the release
with open(output_path, "rb") as f:
    release.upload_asset(output_path, args.output, f.read())
