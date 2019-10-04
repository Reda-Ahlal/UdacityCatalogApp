
# Movies Catalog App

The second project in Udacity's full stack web development nanodegree program.

## Project Overview

The objective of this project is to create an application that provides a list of **items** (Movies) within a variety of **categories** (pre-defined) as well as provide a **user registration and authentication system**.

Registered users will have the ability to **post, edit and delete** their own items.

The application provides also a **JSON endpoint**.

## Software Requirements

* [Python 2.7](https://www.python.org/download/releases/2.7/)
* [VirtualBox](https://www.virtualbox.org/.)
* [Vagrant](https://www.vagrantup.com/)

## 3rd Party Authentication Provider

The application allows a user to log in via a Google  account via a login button in the header of each page.

## Setting up the project

* Install [Python 2.7](https://www.python.org/download/releases/2.7/)
* Install [VirtualBox](https://www.virtualbox.org/.)
* Install [Vagrant](https://www.vagrantup.com/)
* Clone the [fullstack-nanodegree-vm](https://github.com/udacity/fullstack-nanodegree-vm) repository
* Unzip and Copy/paste the content of this current directory (catalog-app) to fullstack-nanodegree-vm/vagrant/catalog directory
* On terminal navigate to fullstack-nanodegree-vm/vagrant/
* To launch the Vagrant VM, type `vagrant up`
* Once it is up and running, type `vagrant ssh`
* type `cd /vagrant/catalog`
* Run the application  `python application.py`
* Access and test the application by visiting http://localhost:5000 locally


## API Endpoints

Aggregated catalog data can be downloaded via API endpoints JSON:

*http://localhost:5000/Catalog/json
*http://localhost:5000/Movies/json
*http://localhost:5000/"movie_name"/json
