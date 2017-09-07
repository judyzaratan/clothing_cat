# Item Catalog #

## Description ##

  An application that displays categorized items.  This application utilizes Google Sign in for authentication and registration for users.  Registered users have the ability to create, edit, or delete items.  

## Requirements ##

* [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* Python 2.7
* For OAuth, register and sign in an application under Google
  1. Add an application for Google Sign in
  2. Create a client_secrets.json
  3. In `/templates/login.html`
     `<div id ="signInButton"></div>`,
     replace data attribute *"clientid"* with your *cliend_id*  provided by Google.  

## Installation ##

1. Fork or clone [item-catalog] repository to your workstation
2. In terminal, go into item-catalog folder
3. Run following vagrant commands to allow VM to install required dependencies, set up environment.
(Side note: Vagrantfile was copied from Udacity's FSND VM repository [here](https://github.com/udacity/fullstack-nanodegree-vm))

  ```
  vagrant up
  ```

4. Log into virtual machine

  ```
  vagrant ssh
  ```

5. After VM is up and running, change directory access repository files

  ```
  cd /vagrant
  ```

6. Within virtual machine terminal, to see application in action, type following command:

  ```
  python project.py
  ```

7. Open browser and type in: http://localhost:5000

#### Optional ####

To allow view website with data, you may fill the database with database populator.

Run the following command after step 5 and continue with step 6 thereafter.
```
python db_populator.py
```

## API Endpoints ##

Request                      | Return
---|---
/catalog/json| Get all categories and their items
/category/__category_id__/item/json| Get items for a particular category with given category integer
/category/__category_id__/item/__item_id__/json| Get information for a particular item with a given category and item ids
