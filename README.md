#Swiss Tournament Generator

First of all, you must install some software in your computer:

Installation
**Git** [docs](https://git-scm.com/doc) | [download](http://git-scm.com/downloads) |
**Virtual Box** [docs](https://www.virtualbox.org/wiki/Documentation) | [download](https://www.virtualbox.org/wiki/Downloads)|
**Vagrant** [docs](https://docs.vagrantup.com/v2/) | [download](https://www.vagrantup.com/downloads)

    Steps:

1. Open terminal:
  - Windows: Use the Git Bash program (installed with Git) to get a Unix-style terminal.
  - Other systems: Use your favorite terminal program.
2. Change to the desired parent directory
  - Example: `cd Desktop/`
3. Using Git, clone the VM configuration:
  - Run: `git clone http://github.com/udacity/fullstack-nanodegree-vm fullstack`
  - This will create a new directory titled *fullstack* that contains all of the necessary configurations to run this application.
4. Move to the *vagrant* folder by entering: `cd fullstack/vagrant/`
5. Using Git, clone this project:
  - Run: `git clone https://github.com/JaviMelo/tournament.git tournament`
  - This will create a directory inside the *vagrant* directory titled *tournament*.
6. Run Vagrant by entering: `vagrant up`


    Usage:

Once the installation steps are complete, you are ready to connect to the
Vagrant box.  To connect:

1. Log into Vagrant VM by entering: `vagrant ssh`
2. Move to *tournament* directory by entering: `cd /vagrant/tournament/`
3. Create the *tournament* database by entering: `psql -f tournament.sql`
>**Note:** You can run `psql -f tournament.sql` at anytime to completely delete the database and start over.

4. If you would like to test the database against Udacity's criteria, enter: `python tournament_test.py`
>**Note:** To clear the database after running tournament_test.py, you can either call the deletePlayers() and deleteMatches() functions or refer to step 3.

5. Launch Python command line by entering `python`
6. Import tournament by entering: `import tournament`
7. Execute a desired function.

Enjoy!