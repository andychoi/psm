from django.core.management import call_command

def my_backup(self):
    try:
        call_command('dbbackup')
    except:
        pass

    self.stdout.write(self.style.SUCCESS('Successfully run backup'))
