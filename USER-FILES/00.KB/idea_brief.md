# Idea brief


The purpose of this script is to take create md files just like this example:
"/Users/ruben/Nextcloud/08_-_DEVELOPMENT/GENAI_IMAGE_TOOLS/img-to-img-zipper/USER-FILES/07.TEMP/example1.md"


The source of the content of these md files are a text file with a link to an image, and a text file with the text that should be placed in the codeblock in the the md files. 


The script should start by creating a subfolder in the 05.OUTPUT folder that is named [YYMMDD_HHMMSS_IMG-TO-IMG_MD]. 
The script then enters this dir:
"/Users/ruben/Nextcloud/08_-_DEVELOPMENT/GENAI_IMAGE_TOOLS/img-to-img-zipper/USER-FILES/04.INPUT/04.1.LINKS"
The script should take the natsort order and take the first text file which contains a URL to an image. 

This image should be the embedded image in the MD doc. 

The script should then go into this dir:
"/Users/ruben/Nextcloud/08_-_DEVELOPMENT/GENAI_IMAGE_TOOLS/img-to-img-zipper/USER-FILES/04.INPUT/04.2_PROMPTS"

The script should take the first text file accordiing to natsort and then take the content of that text file and make it the content of the codeblock in the markdown file. Just as shows shown in the exampel :

"/Users/ruben/Nextcloud/08_-_DEVELOPMENT/GENAI_IMAGE_TOOLS/img-to-img-zipper/USER-FILES/07.TEMP/example1.md"


Then the markdown is saved in created subfolder in 05.OUTPUT. 

Then the script does the same process again with the 2nd text file in the links folder and the prompts folder. 
It does this until all the text files have been turned into markdown files. 

My philosophy is fail fast so if there are any issues then the script should fail loud and fast, and create a FAILURE.MD in the output subfolder and explain what whent wrong. 

The script should not run if the number of text files in the links folder and the prompts folder are not matching. There might be other files in there but if they are not .txt the script should just ignore it. §
