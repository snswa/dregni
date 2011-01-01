# encoding: utf-8
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models

class Migration(SchemaMigration):

    def forwards(self, orm):
        
        # Removing unique constraint on 'Event', fields ['start_date', 'slug']
        db.delete_unique('dregni_event', ['start_date', 'slug'])

        # Deleting field 'Event.slug'
        db.delete_column('dregni_event', 'slug')


    def backwards(self, orm):
        
        # We cannot add back in field 'Event.slug'
        raise RuntimeError(
            "Cannot reverse this migration. 'Event.slug' and its values cannot be restored.")

        # Adding unique constraint on 'Event', fields ['start_date', 'slug']
        db.create_unique('dregni_event', ['start_date', 'slug'])


    models = {
        'dregni.event': {
            'Meta': {'ordering': "('start_date', 'start_time', 'end_date', 'end_time')", 'object_name': 'Event'},
            'description': ('django.db.models.fields.TextField', [], {}),
            'end_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'end_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'site': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['sites.Site']"}),
            'start_date': ('django.db.models.fields.DateField', [], {}),
            'start_time': ('django.db.models.fields.TimeField', [], {'null': 'True', 'blank': 'True'}),
            'tags': ('tagging.fields.TagField', [], {}),
            'title': ('django.db.models.fields.CharField', [], {'max_length': '255'})
        },
        'sites.site': {
            'Meta': {'ordering': "('domain',)", 'object_name': 'Site', 'db_table': "'django_site'"},
            'domain': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        }
    }

    complete_apps = ['dregni']
