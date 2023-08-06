from orator.migrations import Migration


class AddTokenAuthentication(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('oauth_tokens') as table:
            table.increments('id')
            table.integer('user_id').unsigned()
            table.foreign('user_id').references('id').on('users')
            table.string('name')
            table.string('scope')
            table.string('token')
            table.timestamps()

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('oauth_tokens')
