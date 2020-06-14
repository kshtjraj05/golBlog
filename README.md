# golBlog
A blogging search engine delivering results from various sites using elasticsearch and scraping tools like BS and Selenium along with all blogging functionalities of a blog website created using Flask micro-framework.
# Steps to Run
 1. Download and install Docker from https://docs.docker.com/get-docker/
 2. Open the CMD/terminal with sudo/admin privileges.
 3. Change diretory to /golblog
 4. Run command : `docker build -t golblog:latest`
 5. It will take about an hour for the docker image to be created
 6. When the docker image is ready, run command: `docker images` to check if it is created or not
 7. To run image: `docker run --name golblog -p 8000:5000 --rm -e SECRET_KEY=<your secret key> -e SQLALCHEMY_DATABASE_URI=sqlite:///site.db -e EMAIL_PASS=<your email password> -e EMAIL_USERNAME=<your email username> golblog:latest
