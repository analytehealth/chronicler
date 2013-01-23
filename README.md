Chronicler
==========

A Django App for preserving revisions of modified Model Objects

Advantages
----------

There are already a number of revisioning applications for Django out there,
but all of them have various limitations. The goal of chronicler was to handle
tracking changes to many-to-many relations on a model in a more manageable
manner. 

The primary way that `chronicler` works is by inspecting the information
coming into a view, grabbing a stale object, letting the view process,
and then comparing the stale object to the newly created one. This is made 
easiest by the decorator supplied by the package. Please see the Usage section
for more information on how it works.

Installation
----------

To install via pip:

    pip install chronicler

Or to grab the latest from source:

    pip install -e git+git://github.com/analytehealth/chronicler.git#egg=chronicler

To install manually, clone the repository and run:

    python setup.py install

After the package is installed, you'll want to add 'chronicler' to your 
INSTALLED\_APPS in your Django project's settings. From there, you'll want 
to run `syncdb` or if you're using South you'll want to run migrations.

Usage
----------

The primary method of usage for this tool is to leverage the decorator on views
where the Model you wish to track will change. If you had a view that accepts
POSTs to a form to change your model, you could use it like so:

    from chronicler.decorators import audits

    @audits(YourModel, ['relation_set', 'another_set'], 'pk', 'incoming_pk', 'POST')
    def your_update_view(request):
        # modifications

The first arg to the decorator is the model that we're tracking changes on. The
second argument is the list of relations we need to traverse in tracking any
incoming changes. The third argument is the field we should use to look up the
existing object by, and the fourth is the key we should inspect in the incoming
GET/POST data for the value we use to look up our object. Finally, the last 
argument dictates if we should look in GET or POST for our data. Optionally, 
you can pass "force=True" to the decorator to create an audit trail everytime
this view is properly processed. This disables the check `chronicler` makes
to ensure there are actually differences between old and new.

After the view is processed properly, you should end up with a new AuditItem
object in your database:

    from chronicler.models import AuditItem
    audit_item = AuditItem.objects.filter(content_object=your_object).latest()

AuditItems have a @property of audit\_data. That returns a JSON representation
of the data at the time the snapshot was taken. Inside there you'll find your
historical data and can use it as you wish.
