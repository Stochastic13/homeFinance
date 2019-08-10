# homeFinance

This is the homepage of a homegrown finance app for home finances, meant for all open-source & homely homies homing about in a quest for a tool to manage their finances. :)

### Explanation of the financial model
This program uses a weird but hopefully intuitive system (inspired from other Money Management Apps). Every transaction has 4 important descriptors. First, is the **"From"** section, which is one of the *Accounts* (Coming ahead). Next is the **To** section which is either a *Payee* or an *Account*. Next is a **Category** and the final is the **Type**, which is one of the three (*Transfer*, *Minus*, *Plus*).

All the assets and money accounts are modelled under *Accounts*. One would ideally have a Bank Account, Credit Card account, Cash Account and online wallets/cryptocurrency wallets as a part of his/her *Accounts* list. If you total the balance of these Accounts, you would get the current total wealth of the person, the sum total of their money. If you shuttle money between these accounts, (Example: Paying the Credit Card bill is Money goes from Bank Account to Credit Card Account), the **Type** *Transfer* is used for the transaction.

*Payees* are the entities which one would deal with financially, either paying money to or getting money from. If one pays moeny to a payee, the transaction **Type** is *Minus*, and it goes from one account to a payee. If one is paid some money, the **From** and **To** fields are still an account and a payee respectively, but the **Type** changes to *Plus*.

*Categories* are just a way to classify transactions. Each transaction can be labelled with a category irrespective of all other fields. For example, a *transfer* modelling the payment of Credit Card Bills can be labelled with a category "bills". A *Minus* transaction from Paypal to Amazon to buy a phone can be labelled with the category "electronics", and so on.

There is no standard way to model your finances. This is just a rough guide. Feel free to create whatever system suits you the best.
![The model used in the app](demo.png)

### Description of the app
....upcoming....

### Why should I use this app?
...upcoming...
### Bad reasons to use this app
...upcoming...
### Upcoming Features
...upcoming...




### Requirements (apart from Python 3.x)
1. [Cryptography](https://pypi.org/project/cryptography/) (Cool Stuff, I know)
2. [Pandas](https://pypi.org/project/pandas/)
3. [Numpy](https://pypi.org/project/numpy/)
4. base64, os, sys, tkinter, time, getpass (Usually included as the standard python library)
