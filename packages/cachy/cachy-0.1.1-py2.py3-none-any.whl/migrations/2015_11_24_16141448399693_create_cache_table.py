from orator.migrations import Migration


class CreateCacheTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('cache') as table:
            table.string('key').unique()
            table.text('value')
            table.integer('expiration')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('cache')
