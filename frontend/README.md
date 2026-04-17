# terra
# Pictures
- file type = .jpg
- file size (max)  = 500 kb
- resolution
- slide show aspect ratio 16:9
- Photos export settings 2000pix width 80% quality

#Banners
- 16:9
- 2000x1125
- jpg
- 80% quality

# Web Server Install
## Update Server  
'sudo apt update'
'sudo apt upgrade'

## Install and Setup Webserver
- 'sudo apt install nginx'
- Create directory for site - 'mkdir /home/www/terra'
- Configure web server



#Upgrade NodeJS to latest long term release
- install nvm and make sure NodeJS is not already installed, if so delete it
- nvm install lts


`sudo apt install npm`




# React.js

set env variable %PUBLIC_URL% to point a the public directory in the project.

npm add bootstrap
npm start
npm install --save react-router-dom


- Install node.js https://nodejs.org/en/
Go to your project folder in the terminal, and paste these two commands:
- Step 1: Run `npm init -y`
- Step 2: Run `npm install`

- Create a folder called src and run this terminal command:
This will generate the JS so it needs to be running while developing.
'npx babel --watch src --out-dir ./public/js/react --presets react-app/prod'


## Install packages
- Add React Modal 
`npm install --save react-modal`

### Add react-photo-gallery
'npm config set legacy-peer-deps true'  (this allows you to install the gallery eventhough it has some legacy deps.)
'npm i'
'npm i react-photo-gallery'

### Install JQuery
'npm install jquery --save'




# Postgresql
Install Postgresql for React: https://blog.logrocket.com/getting-started-with-postgres-in-your-react-app/

log into pgsql: sudo -i -u postgres
CREATE ROLE my_user WITH LOGIN PASSWORD 'my_pass';
alter role torsten CREATEDB;


# Keeping THings Running
- See outdate dependencies:
- npm outdated or npm update [package]

Windows needs  to allow scripts to run or it will yell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser