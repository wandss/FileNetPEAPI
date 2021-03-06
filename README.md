# FileNetPEAPI
This is a Python API for using FileNet Process Engine (Case Foundation).

Package name: fnetpepAPI

This document explains how to use this API.
It is important to have some knowledge on some Process Engine concepts like:
**App Spaces, Roles, Workbaskets, Queues etc.**

Obviously knowing **[Python](https://www.python.org/)** will help.

This API requires [Requests](https://github.com/kennethreitz/requests) by Kenneth Reitz, so install it before.

*Note: If using the setup.py script, Requests will be automatically installed*

**Important!!!!**

**- At this point, this API is only working with Python2 version.**

## Installing the fnetpepAPI:
Download this package or run:
```shell
git clone https://github.com/wandss/FileNetPEAPI.git
```
Inside the created directory (FileNetPEAPI) run:
```shell
python setup.py build 
python setup.py install
```

## Running the API:
```python
from fnetpepAPI.fnetpepAPI import PEClient, PE
```
### To create a "connection":
```python
client = PEClient('server_name', 'server_port', 'user', 'passwd')
```
*Sample: client = PEClient('content_engine_server_address', '9080', 'p8admin', 'password').*

With this instance of PEClient is possible to check some variables like:

#### Available App Spaces:
*Prints appspace names*
```python
apps = client.apps
print apps
```
#### Available Workbasket:
*Prints a list with Workbasket names.*
```python
wbs = client.workbaskets.keys()
print wbs
```
#### Available Roles:
*Prints a python dictionary with Appspace and its roles*
```python
roles = client.roles
print roles
```
#### Available Workflow:
*Prints available workflow names*
```python
wf_names = client.workflow_classes.keys()
print wf_names
```
### Now, create a "PE" object:
To do so, is required to pass an **instance from PEClient**.
```python
pe = PE(client)
```
### With a PE object is possible to retrieve information from a workbasket and manage tasks:

*Get all tasks from all Workbaskets:*
```python
all_tasks = pe.getAllTasks()
```
*Above, a python list containning python dictionaries (tasks), will be returned.*

*Get logged user's Inbox Queue:*
```python
inbox_queue = pe.getInboxQueue()
```
*Get a specific Queue from a Workbasket*
```python
my_queue = pe.getQueue('workbasket_name')
```
or
```python
my_queue = pe.geQueue(wbs[index])
```
*Get tasks from a particular Queue:*
```python
tasks = pe.getTasks(my_queue)
```
*Other example*:
```python
inbox_tasks = pe.getTasks(inbox_queue)
```
*Listing the amount tasks in a Queue*:
```python
inbox_queue.get('count')
```
### Tasks are the final objects from a Queue. Is possible to interact with them and doing the following actions:

- Show information from documents attached to the task,
- Show comments, 
- Add comment to a task, 
- Search Directory service for users,
- Search Directory service for groups,
- Reassign a task to other user, 
- Returning a task to the it's original Workbasket,
- Locks a task, so other users can’t interact with it while you're working, 
- Unlocks the task without saving any modifications, 
- Finishing the task,
- Starting (Launching) a Workflow,
- Retrieve a Step from a task,
- Retrieve required data from a Step,
- Retrieve responses,
- Updating a Task,

## Showing information from tasks:
*You can iterate tasks:*
```python
for task in tasks:      
      pe.some_action(task)
```            
*Or work with a specific task*:
```python
task = tasks[0]
```
*Showing Information from a task:*
```python
info = pe.showTaskInfo(task)
for k, v in info.items():
	print '%s: %s'%(k, v)
```
*Showing Attachments Information from a task:*
```python
attached_doc = pe.getAttachmentsInfo(task)
for k, v in attached_doc.items():
	print '%s: %s'%(k, v)
```
*Showing Comments from a task:*
```python
comment = pe.getComment(task)
print comment
```
## Adding comment to a task:
```python
task = pe.saveAndUnlockTask(task, u'This is a Comment')
```
*Important: When adding comments, the updated task will be returned. Also important, to avoid issues with special characters, 
prefer use **unicoded text (u'Text')** and not pure string objects.*
## Search Directory Service for users:
*Given a string the API will return a list with users who match the passed string or a message informing that the User wasn't found.*
```python
user = pe.getUser('username')
print user
```
## Search Directory Service for groups:
*Given a string the API will return a list with groups that match the passed string or a message informing that the User wasn't found.*
```python
group = pe.getGroup('group_name')
```

## Reassigning a task:
*To reassign a task, a destination user must be informed:*
```python
reassign = pe.reassignTask(task, 'new_user')
```
*It is also possible to add a comment before reassigning a task, like:*
```python
reassign = pe.reassignTask(task, 'new_user', u'Hello. Your attention is required for the attached Document!')
print reassign
```
*When reassigning a task, the destination user will be checked (added on version 1.2.0) on the Directory Service. If the user is not found, a message informing that will be returned to the "reassign" variable as showed above.*
```python
reassign = pe.reassignTask(task, 'new_user')
print reassign
>>> "User 'new_user' not found in Directory Service"
```
*When interacting with a task it will be automatically locked, so you might need to unlocks it by issuing:*
```python
pe.abort(task)
```
## Returning a task to it's original Workbasket:
*If a task has been moved between workbaskets (queues) or moved from one workbasket to user's Inbox, is possible sending it back to it's original workbasket. It is also allowed to insert a comment before sending it back.
A task must be passed. If the task can't be moved back to it's original workbasket or if it already is there, a message informing this will be returned.*
```python
pe.returnToSoruce(task) #no comment
pe.returnToSource(task, "Here some explanatory message")
```
## Finishing a task:
*Finishing a task is the same of finishing a step. If the step is the last of the workflow, the workflow might be finished.
It is also possible to pass a comment before finishing the step*
```python
pe.endTask(task) #no comment passed.
```
```python
pe.endTask(task, u'Any comment you like') #comment passed.
```
## Starting (Launching) a Workflow:
Starting (launching) a worflow could be a little bit complex, since each workflow is created with specific needs and settings.
It is possible to have a workflow that needs a destination user to be set and others that already has a specified destinated user.
Sometimes, when creating a workflow, there might be some datafields to be filled in or documents to be attached at launch step.
There are many possibilities here and each one of them depending on the workflow itself.

So, since each Workflow has its needs, the first thing is to understand what are the needs from that workflow, to do this run:
```python
launched = pe.startWorkflow(wf_name = 'WorkFlowName')
```
*You must run this with the wf_name property. Not doing so, will return the message:*
**"There's no 'wf_name' key on dictionary or the WorkFlow name doesn't exist."**
To find out Workflow names, issue (as mentioned above):
```python
client.workflow_classes.keys()
```
After properly issuing the *"wb.startWorkflow(wf_name = 'WorkFlowName')* as shown earlier, depending on the workflow's settings,the options to be printed out can be:
- Data Fields Names
- Workflow groups Names
- Attachment Name Field

Usually IBM packages two basic "Document Approval" sample workflows within FileNet:
- ICNSequentialDocumentApproval,
- ICNParallelDocumentApproval

## Practical example:
*When running:*
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval')
```
Aside printing the information, the above command, will return a dictionary to 'launched' variable 
containing the same printed information.
You can check this by issuing:
```python
for k, v in launched.items():
	print (k)
	print ('\n').join(v)+'\n'
```
*The printed result is*:
```
To Create this Workflow, you'll probably need to provide below data:
ICN_TeamspaceId
ICN_WFDeadlineDate
ICN_AllowReassign
ReturnToSender
ICN_Instructions
FinalReview

Groups to be populated with users:
Approvers

Available Attachment Fields:
DocumentforReview
```
**Explaining above info:**

```
- ICN_TeamspaceId
- ICN_WFDeadlineDate
- ICN_AllowReassign
- ReturnToSender
- ICN_Instructions
- FinalReview
```
*These are data fields availabe for the workflow. It doesn't mean that all of this data fields must be filled in. It will depends on how the worflow was written, but this shows which data fields exists on this particular Workflow.*
```
- Approvers
```
*This is a group to be populated with one, many users or directory groups.*
```
- DocumentforReview
```
*Finally, this is the field to be used when attaching a document.*

### Samples for starting this specific workflow:
#### Sending to one user:
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval', Approvers='destinated_user' )
```
*Only informed one destination user.*
#### Sending to more users:
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2' )
```
*To send for more than one user, write user_names separated by ', ' (comma and space) like:*
**Approvers = 'user1, user2, ..., userX'**
*It is also possible to use Directory Groups as parameter*

#### Setting users and values for data field:
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2',
                            ICN_Instructions='Here some instructions',
                            ICN_AllowReassign=True                            
                            )
```
***When using Data Fields, the type passed for the value here must match the type written in workflow.
In the above example "ICN_AllowReassign" was created in workflow as a boolean type, so here we must match the same type by passing True (boolean type) and not 'True'(string type)***

#### Setting users, values for data field and attaching a document:
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2', 
                            ICN_Instructions='Here some instructions',
                            ICN_AllowReassign=True, DocumentforReview="{Filenet's Document ID}",
                            object_store='ObjectStoreName', subject="New Document for review"
                            )
```
If no exceptions were raised, the **launched** variable will now have the Workflow Number (wobnum).
***Only documents available in FileNet repository can be attached, therefore the ID for this document must be passed here. It is also required to pass the object_store key with the desired 'ObjectStoreName'
It is also available to set a subject for this Workflow by passing the parameter subject, with any string you like as value.***

As shown rigth above, starting (lauching) a workflow relies on many variables. Therefore is important to know the workflow that's about to be started.

### Commum atributes for any workflows are:
- wf_name **(required)**
- subject

Any other attribute depends on the Workflow's settings.

## Retrieve a Step from a task:
As explained before, a task is the final object in a queue. A group of tasks are called queue. Steps therefore, are the objects inside a task, meaning a task is formed from a group of steps. A step works like the Lauch Step so is possible to interact with steps, setting values, making choices like when creating a workflow. 

To get a step a *task* must be passed like:
```python
step = pe.getStep(task)
```
Each step has it's specifc needs and may or may not have options that needs attention.

## Retrieve required data from a Step:
Usually, steps might have:
- Data Fields,
- Workflow Groups,
- Attachment Fields,
- Responses.

The three first options works just the same way as when starting a Workflow. For steps though, they have different "permissions" they might have *read*, *write* or *read and write* permissions.

***Responses*** though are only available on steps and are used to offer users choices within a task, like "Approve" or "Reject".
When retrieving information from a step with the below method, only the *writable* ones will be returned.
Usage:
```python
step_info = pe.getStepInfo(task)
```
By printing the *step_info* variable, a Python dictionary like the one below will be shown:
```python
{'Available Data Fields': [u'Licence_Plate'], 'attachments': [u'References'], 
'selectedResponse': [u'Approve', u'Reject']}
```
For the above example, for going to the next step in the task, it is required to choose between *Approve* and *Reject*, theese are the available **Responses**. A value for **Licence_Plate** will also be needed, but not required.
Also, for this example *"References"* is a field that allows user to attach a document, but are not required.

## Retrieve Responses:
It is possible to directly check if there are responses for the task:
```python
responses = pe.getResponses(task)
```
A list with all available responses will be returned. The response name in this list will be used as value for the attribute *selectedResponse* when updating the task.

## Updating a Task:
As explained in this documentation, for moving to the next "step" in a task, just use the **"endTask()"** method. When a task has *responses* though, an exception will be raised. **(to be applied in next Version, right now the message *"This task needs to be updated. Check the updateTask method."* will be returned)**.
If everything is ok, the updated task will be returned. 
Based in the above example, do as follows:
```python
task = pe.updateTask(task, selectedResponse='Approve', Licence_Plate='Pyth-0000')
```
*When the step has "reponses" the **selectedResponse** attribute **must** be provided, like the "wf_name" when starting a workflow.*
*The value set for attributes in for data fields, must match the expected type in the workflow, otherwise a exception will be raised.*
In the example "Licence_Plate" is set in workflow as a string, so a string must be passed here.

### Updating Datetime Fields:
**In the next version, some validation for datetime fields will be applied**
**It will be required a datetime object**

Now, the updated task can be used with the **"endTask(task)"**

## Notes on this program:
Obviously there are many things to improve at this API (and probably some bugs). Yet, at the state it is now, I do believe it can be shared, since I've already used it to implement at least other trhee different applications and they are working just fine.

As metionend at the top of this document, this API (untill now) will only work with Python 2.x versions.

I do hope this API can be useful for those who intends to develop FileNet application as it has been to myself.

This API aims the "Process Engine" only (Case Foundation). To expand it's usage and use Python to access "Content Engine" as well, I do recommend the **Open CMIS API**.

Open CMIS is an amazing API for accessing and controlling objects inside a CMIS Compliant repository.
It is distributed and maintenned by Apache, [Apache Chemistry](http://chemistry.apache.org/python/cmislib.html) and written by Mr. [Jeff Pots](https://github.com/jpotts)

Open CMIS works with most of CMIS Compliant Repository, therefore is possible to use it not only with FileNet, but also with Alfresco, Open TEXT, Share Point and many others.

[Python documentation for cmislib](https://chemistry.apache.org/python/docs/), the Open CMIS for Python package.

To use Open CMIS with FileNet is required to have IBM CMIS installed.
There's a tutorial from IBM using Open CMIS available [here](http://www.ibm.com/developerworks/library/x-cmis1/)

## About Versions:

### Version 1.0.0: 
- Initial version.

### Version 1.1.0: 
- Added functionality for returning a task to it's original workbasket.

### Version 1.2.0: 
- Created functionality for searching Users in Directory Service.
- Now the user is validated before a task can be reassigned.

### Version 1.3.0: 
- Created functionality for searching Groups in Directory Service.
- Created functionality for updating values and selecting available responses in steps.

#### Version 1.3.1: 
- When starting a workflow, now the **"startWorkflow()"** method will raise an exception for errors or return the number for the started Workflow **(Work Object Number - WobNum)**
