# combattb_web
A Web interface to the COMBAT-TB Neo4j Graph Database

### Installation
**NB: We assume you have a running instance of the Graph DB**

**Clone this repository:**

    $ git clone git@bitbucket.org:sanbidev/combattb_web.git
    $ cd combattb_web

**Create a virtualenv, and activate it:**

    $ virtualenv ctbweb 
    $ source ctbweb/bin/activate

**After that, install all necessary dependencies by running:**

    $ pip install -r requirements.txt
    $ pip install -U git+https://github.com/SANBI-SA/vcf2neo.git#egg=vcf2neo
    $ npm install
    $ bower install
    
**Then, run the application:**

	$ python run.py
    
**To see CombatTbWeb, access this url in your browser:** 

	http://localhost:5000
	
### Running CombatTbWeb inside a [Docker](https://www.docker.com/) container

*To run CombatTbWeb inside a Docker container, you need to have [Docker installed](https://docs.docker.com/installation/ubuntulinux/). Then:*
     
**Build the image using:**

    $ docker build -t docker-combattb . 
   
**Run the image:**
    
    $ docker run -it -p 5001:5000 --name combattb-on-docker docker-combattb
    
**Access CombatTbWeb on `0.0.0.0:5001`:** 
        
    http://0.0.0.0:5001/