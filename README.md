# FileNetPEAPI
A Python API for using FileNet Process Engine (Case Foundation)

This document explains how to use this API.
Is important to have some knowledge on some Process Engine concepts like Queues, Roles, Workbaskets, etc.

Obviously knowing Python will help.

This API requires [Requests](https://github.com/kennethreitz/requests) by Kenneth Reitz, so install it before.

###Running the API:
```python
from pythonPERest import PEClient, WorkBasket
```
###To create a “connection”:
```python
client = PECLient(‘server_name’, ‘server_port’, ‘user’, ’passwd’)
```
Sample:
*client = PEClient(‘content_engine’, ‘9080’, ‘p8admin’, ’password’)*
With This client instance of PEClient  you can check:

####Available App Spaces:
```python
client.apps
```

####Available Queues:
Prints a list with queue_names.
```python
client.queue_names
```
####Available Roles:
```python
client.roles
```
####Available Workflow:
```python
client.workflow_classes.keys()
```
###Now create a Workbasket object:
To do so, is required to pass an instance from PEClient and a queue name.
The available queues can be obtained as shown above.
If no queue_name is passed, the program will inspect the ‘Inbox’ for the connected user.
```python
wb = WorkBasket(client)
```
###With a WorkBasket object is possible to retrieve:
Information from a workbasket:
*Prints the url for the workbasket that is been used.*
```python
wb.url
```
*Prints all the tasks available in the Queue for the given workbasket:*
```python
wb.getElementsCount()
```
To get all the tasks from this queue:
Here a list with tasks will be returned.
Each task inside this list is a python dictionary object.
```python
tasks = wb.getTasks()
```

###Tasks are the final objects from a Queue. Is possible to interact with them and do the following actions:
Reassign the task to other user, add a comment, lock it so other users can’t interact with it, unlock it without save modifications, show comments, show information from a task, show information from documents attached to a specific task.

####Showing information from tasks:

#####You can iterate tasks:
```python
for task in tasks:      
      wb.showTaskInfo(task)
```            
####For working with a specific task:
```python
task = tasks[0]
```
Showing Information for a task:
```python
wb.showTaskInto(task)
```
Showing Comments for a task:
```python
wb. showComment (task)
```
Showing AttachmentsInfo for a task:
```python
wb. showAttachmentsInfo (task)
```
###Reassigning a task:
To reassign a task, a destination user must be informed:
```python
wb.reassignTask(task, ‘new_user’)
```
It is also possible to add a comment like:
```python
wb.reassignTask(task, ’new_user’, ‘Hello. This document needs aproval’)
```
In case you want to add a comment but not reassign a task issue:
```python
wb.saveAndUnlockTask(task, ‘Check this out later’)
```
When interacting with a task it will automatically be locked so you might need to unlocks it by issuing:
```python
wb.abort(task)
```

