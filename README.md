# StreamToDocument
Pulls a user's instagram feed, for search search criteria, and dumps it into a document for them to then edit and print.

# Instructions
1. Ensure you have [Python](https://www.python.org/) installed. This can be checked on the command line as follows:

>$ python --version
>Python 2.7.6

2. Run the script as follows:

> Usage: python stream_to_document.py -t [End Date] -o [File] -f [Start Date]
>
> End Date - End Date to search to, format DD/MM/YYYY
> File - HTML file to write to
> Start Date - Start Date to search from, format DD/MM/YYYY

An example would be:

> $ python stream_to_document.py -f 01/01/2015 -t 31/01/2015 -o ~/Desktop/test.html

3. Output of the script will be something like this:

> $ python stream_to_document.py -f 01/01/2015 -t 31/01/2015 -o ~/Desktop/test.html
> Please visit the following URL to login. Once complete you will find yourself on our GitHub page. Copy the URL and paste it below then hit enter to continue
> https://api.instagram.com/oauth/authorize/?client_id=418b90ba16fe4ab3a55727087d8d845b&redirect_uri=https%3A//github.com/igkuk7/StreamToDocument&response_type=token
> Result URL:

Visit the URL in the output. This will take you to the instagram website to login and then authorise StreamToDocument to access you posts. Once done you will be sent to [StreamToDocument Home Page](https://github.com/igkuk7/StreamToDocument). On that page copy the URL and paste it into the *Result URL* in the script and hit Enter

4. The script will now complete and tell you the file is generated.

> $ python stream_to_document.py -f 01/01/2015 -t 31/01/2015 -o ~/Desktop/test.html
> Please visit the following URL to login. Once complete you will find yourself on our GitHub page. Copy the URL and paste it below then hit enter to continue
> https://api.instagram.com/oauth/authorize/?client_id=418b90ba16fe4ab3a55727087d8d845b&redirect_uri=https%3A//github.com/igkuk7/StreamToDocument&response_type=token
> Result URL: https://github.com/igkuk7/StreamToDocument#access_token=1635247040.418b90b.d30cce44f28c47f5a6ddae5e49a77bdd
> Generated HTML file: /home/iaink/Desktop/test.html

Open the generated HTML file in a web browser and it will contain images from your stream with dates and captions beneath each.