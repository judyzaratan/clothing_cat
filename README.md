## Item Catalog ##
------
### Description ###
------
### Requirements ###
------
* [Virtualbox](https://www.virtualbox.org/wiki/Downloads)
* [Vagrant](https://www.vagrantup.com/downloads.html)
* Python 2.7


### Installation ###
___

1. Fork or clone [item-catalog] repository to your workstation
2. In workstation terminal, go into item-catalog folder
3. Run following vagrant commands to allow VM to install required dependencies, set up environment.

`vagrant up`

4. Log into virtual machine

`vagrant up`

5. After VM is up and running, change directory access repository files

`cd /vagrant`

6. Within virtual machine terminal, to see application in action, type following command:
`python project.py`

7.
http://localhost:5000

##### Optional #####
To allow view website with data, you may fill the database with database populator.

Run the following command after step 5.
`python db_populator.py`

### API Endpoints ###
-----------------------------
|Request                      | Return
|--------:-------------------:--------------------|
|/catalog/json| Get all categories and their items|
|/category/__category_id__/item/json| Get items for a particular category with given category integer|
|/category/__category_id__/item/__item_id__/json| Get information for a particular item with a given category and item ids|
