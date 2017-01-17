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

##Installing the fnetpepAPI:
Download this package or run:
```shell
git clone https://github.com/wandss/FileNetPEAPI.git
```
Inside the created directory (FileNetPEAPI) run:
```shell
python setup.py build 
python setup.py install
```

##Running the API:
```python
from fnetpepAPI.fnetpepAPI import PEClient, PE
```
###To create a "connection":
```python
client = PEClient('server_name', 'server_port', 'user', 'passwd')
```
*Sample: client = PEClient('content_engine_server_address', '9080', 'p8admin', 'password').*

With this instance of PEClient is possible to check some variables like:

####Available App Spaces:
*Prints appspace names*
```python
apps = client.apps
print apps
```
####Available Workbasket:
*Prints a list with Workbasket names.*
```python
wbs = client.workbaskets.keys()
print wbs
```
####Available Roles:
*Prints a python dictionary with Appspace and its roles*
```python
roles = client.roles
print roles
```
####Available Workflow:
*Prints available workflow names*
```python
wf_names = client.workflow_classes.keys()
print wf_names
```
###Now, create a "PE" object:
To do so, is required to pass an **instance from PEClient**.
```python
pe = PE(client)
```
###With a PE object is possible to retrieve information from a workbasket and manage tasks:

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
###Tasks are the final objects from a Queue. Is possible to interact with them and doing the following actions:
- Show information from a task,
- Show information from documents attached to the task,
- Show comments, 
- Add comment to a task, 
- Search Directory service for users,
- Reassign a task to other user, 
- Returning a task to the it's original Workbasket,
- Locks a task, so other users can’t interact with it while you're working, 
- Unlocks the task without saving any modifications, 
- Finishing the task,
- Starting (Launching) a Workflow,

##Showing information from tasks:
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
##Adding comment to a task:
```python
task = pe.saveAndUnlockTask(task, u'This is a Comment')
```
*Important: When adding a comment, the updated task will be returned. Also important, to avoid issues with special characters, 
prefer passing unicoded text (u'Text') and not pure string objects.*
##Search Directory Service for users:
*Given a string the API will return a list with users who match the passed string or a message informing that the User wasn't found.*
```python
user = pe.getUser('username')
print user
```

##Reassigning a task:
*To reassign a task, a destination user must be informed:*
```python
reassign = pe.reassignTask(task, 'new_user')
```
*It is also possible to add a comment before reassigning a task, like:*
```python
reassign = pe.reassignTask(task, 'new_user', u'Hello. Your attention is required for the attached Document!')
print reassign
```
*When reassigning a task, the destination user will be checked (added on version 1.2.0) on the Directory Service. If the user is not found a message informing that the User wans't found will be returned to the "reassign" variable as showed above.*
```python
reassign = pe.reassignTask(task, 'new_user')
print reassign
>>> "User 'new_user' not found in Directory Service"
```
*When interacting with a task it will be automatically locked, so you might need to unlocks it by issuing:*
```python
pe.abort(task)
```
##Returning a task to it's original Workbasket:
*If a task has been moved between workbaskets (queues) or moved from one workbasket to user's Inbox, is possible sending it back to it's original workbasket. It is also allowed to insert a comment before sending it back.
A task must be passed. If the task can't be moved back to it's original workbasket or if it already is there, a message informing this will be returned.*
```python
pe.returnToSoruce(task) #no comment
pe.returnToSource(task, "Here some explanatory message")
```
##Finishing a task:
*Finishing a task is the same of finishing a step. If the step is the last of the workflow, the workflow might be finished.
It is also possible to pass a comment before finishing the step*
```python
pe.endTask(task) #no comment passed.
```
```python
pe.endTask(task, u'Any comment you like') #comment passed.
```
##Starting (Launching) a Workflow:
Starting (launching) a worflow could be a little bit complex, since each workflow is created with specific needs and settings.
It is possible to have a workflow that needs a destination user to be set and others that already has a specified destinated user.
Sometimes, when creating a workflow, there might be some datafields to be filled in or documents to be attached at launch step.
There are many possibilities here and eache one of them depends on the workflow itself.

So, since each Workflow has its needs, the first thing is to understand what are the needs from that workflow, to do this run:
```python
launchstep = pe.startWorkflow(wf_name = 'WorkFlowName')
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

##Practical example:
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
*This is a group to be populated with one or many users.*
```
- DocumentforReview
```
*Finally, this is the field to be used when attaching a document.*

###Samples for starting this specific workflow:
####Sending to one user:
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval', Approvers='destinated_user' )
```
*Only informed one destination user.*
####Sending to more users:
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2' )
```
*To send for more than one user, write user_names separated by ', ' comma and space like:*
**Approvers = 'user1, user2, ..., userX'**

####Setting users and values for data field:
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2',
                            ICN_Instructions='Here some instructions',
                            ICN_AllowReassign=True                            
                            )
```
***When using Data Fields, the type passed for the value here must match the type written in workflow.
In the above example "ICN_AllowReassign" was created in workflow as a boolean type, so here we must match the same type by passing True (boolean type) and not 'True'(string type)***

####Setting users, values for data field and attaching a document:
```python
launched = pe.startWorkflow(wf_name='ICNSequentialDocumentApproval',
                            Approvers='destinated_user1, destinated_user2', 
                            ICN_Instructions='Here some instructions',
                            ICN_AllowReassign=True, DocumentforReview="{Filenet's Document ID}",
                            object_store='ObjectStoreName', subject="New Document for review"
                            )
```
***Only documents available in FileNet repository can be attached, therefore the ID for this document must be passed here. It is also required to pass the object_store key with the desired 'ObjectStoreName'
It is also available to set a subject for this Workflow by passing the parameter subject, with any string you like as value.***

As shown rigth above, starting (lauching) a workflow relies on many variables. Therefore is important to know the workflow that's about to be started.

###Commum atributes for any workflows are:
- wf_name **(required)**
- subject

Any other attribute depends on the Workflow's settings.

##Notes on this program:
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

##About Versions:

###Version 1.0.0: 
- Initial version.

###Version 1.1.0: 
- Added functionality for returning a task to it's original workbasket.
