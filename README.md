# Referral System

This is the API for the referral system. It's built using flask (python3) and MongoDB.

___Note___: 
1. To run it locally on your machine, create a ```.env``` file and add ```MONGOPWD=<password>``` in it.
2. Main file is ```api.py``` and some helper functions are included in ```helper_functions.py```.

## Installation of relevant libraries

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install all dependencies.

```bash
pip install -r requirements.txt
```
***
## Usage

It would be better to use some API Platform with proper interface, like [Postman](https://www.postman.com/downloads/). However, other ways may work equally good.

Run the Code using
```bash
python3 api.py
```

### Adding a New User
Returns nothing. Just adds the user to the system if the details are valid.
```python
POST http://127.0.0.1:5000/api/enroll?first_name=Person1&last_name=surname&email=email1@gmail.com&password=MyPassword&phone_number=9999999999
```

### Adding a user when Referral Code is also provided
Returns nothing. Just adds the user to the system if the details are valid. Also, makes a transaction for the referral code.
```python
POST http://127.0.0.1:5000/api/enroll?first_name=Person1&last_name=surname&email=email1@gmail.com&password=MyPassword&phone_number=9999999999&referred_by=a71ec160-6aca-412c-830a-0c1606a1501d
```

### Get the Referral Code of the user
Returns the unique referral code of the user in the form of a string
```python
GET http://127.0.0.1:5000/api/referralCode?email=email1@gmail.com
```

### Get the Referral History of the user
Returns the list of all transactions where a new user signed up using this user's referral code. Also mentions the awards this user got after every transaction. 

Note: The email address returned in this transaction are masked.
```python
GET http://127.0.0.1:5000/api/referralHistory?email=email1@gmail.com
```

### Get the Milestones Achieved and not achieved by the user
Returns a list of all milestones, and specifically marks all milestones that are already achieved by the user.
```python
GET http://127.0.0.1:5000/api/milestones?email=email1@gmail.com
```

### Remove the account from the Referral System
Once removed, the user's referrel code will be invalid for all future transactions.
```python
POST http://127.0.0.1:5000/api/withdraw?email=email1@gmail.com
```

### Add a new Milestone into the referral system
Milestones contain the target number of referrals and the corresponding reward on achieving them.
```python
POST http://127.0.0.1:5000/api/addMilestone?referral_count=5&award=500
```
***
## Output
The API returns status code 201 if successful, and 404 if not successful. The response often also consists of the resulting string or JSON object.

## Collections Schema

We have created the following collections within MongoDB database ```API```:
![Database Schema](https://github.com/sak1sham/Referral-System/blob/main/Explanation/Schema%20Planning.png)
