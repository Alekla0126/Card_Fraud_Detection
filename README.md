Youtube Downloader API

This API allows you to download Youtube videos and playlists in different resolutions and formats, and optionally download subtitles.

Installation

Clone this repository to your local machine.
Install the required packages by running pip install -r requirements.txt

. Run the API by running python app.py
. Usage Download a video Send a POST request to /download with the following JSON data:

 {
    "url": "https://www.youtube.com/watch?v=JkORjCt2VhQ",
    "format": "high",
    "subtitles": "False"
}

. url: The URL of the Youtube video you want to download. format: The format of the video you want to download. Valid values are mp4, low, medium, high, and mp3
. subtitles: Whether to download subtitles for the video. Valid values are True and False
. If the video has subtitles and 
subtitles is set to True , the API will return the video file and subtitle file as attachments. Otherwise, the API will return only the video file as an attachment.

If the video does not have subtitles and subtitles is set to True, the API will return a JSON response with the following message:

{
    "message": "This video does not have subtitles."
}

Download a playlist

Send a POST request to /download_playlist with the following JSON data:

{
    "url": "https://www.youtube.com/playlist?list=PLwVUbPpIRn1QxqZz0x9Zt-dNHQVJzJGZ_",
    "format": "high",
    "subtitles": "False"
}

url: The URL of the Youtube playlist you want to download. 
format : The format of the videos in the playlist you want to download. Valid values are mp4, low, medium, high, and mp3.
subtitles: Whether to download subtitles for the videos in the playlist. Valid values are True and False The API will create a directory for the playlist and download each video in the playlist to that directory. If all videos in the playlist are downloaded successfully, the API will create a zip file of the playlist directory and return it as an attachment.

If one or more videos in the playlist do not have subtitles and subtitles is set to True, the API will return a JSON response with the following message:

{
    "message": "One or more videos in this playlist do not have subtitles."
}

Examples

Download a video in the highest resolution and without subtitles
Request:

{
    "url": "https://www.youtube.com/watch?v=JkORjCt2VhQ",
    "format": "high",
    "subtitles": "False"
}

Response:
The video file is downloaded as an attachment.

Download a video in the low resolution and with subtitles
Request:

{
    "url": "https://www.youtube.com/watch?v=JkORjCt2VhQ",
    "format": "low",
    "subtitles": "True"
}

Response:
The video file and subtitle file are downloaded as attachments.

Download a video in the medium resolution and with subtitles, but the video does not have subtitles
Request:

{
    "url": "https://www.youtube.com/watch?v=JkORjCt2VhQ",
    "format": "medium",
    "subtitles": "True"
}

Response:

{
    "message": "This video does not have subtitles."
}

Download a playlist in the highest resolution and without subtitles
Request:

{
    "url": "https://www.youtube.com/playlist?list=PLwVUbPpIRn1QxqZz0x9Zt-dNHQVJzJGZ_",
    "format": "high",
    "subtitles": "False"
}

Response: The zip file of the playlist directory is downloaded as an attachment.

Download a playlist in the medium resolution and with subtitles, but one or more videos in the playlist do not have subtitles

Request:
{
    "url": "https://www.youtube.com/playlist?list=PLwVUbPpIRn1QxqZz0x9Zt-dNHQVJzJGZ_",
    "format": "medium",
    "subtitles": "True"
}

Response:
{
    "message": "One or more videos in this playlist do not have subtitles."
}


License
This project is licensed under the MIT