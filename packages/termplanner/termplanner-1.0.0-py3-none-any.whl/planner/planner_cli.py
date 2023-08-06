import click
from planner.planner import Planner


# This saves the Planner object, used whenever a function needs to pass it.
pass_planner = click.make_pass_decorator(Planner)


class PlannerRunner(object):
    """Gives planner cli commands using click."""

    @click.group()
    @click.pass_context
    def cli(ctx):
        """Creates a planner object which is then held in a context
        object.
        
        :type ctx: :class:'click.core.Context'
        :param ctx: An instance of click.core.Context which stores an
                    instance of the Planner object.
        """
        ctx.obj = Planner()
        
# This is mostly here for reference.
#    @cli.command()
#    @pass_planner
#    def run(planner):
#        """This is the doc string for the run command"""
#        click.echo("This is working")
#        click.echo(planner.check_string())

    @cli.command()
    @click.argument("date", default="5.7.2000")
    @click.argument("event", default="Alex Hurtado's birthday")
    @click.argument("database", default="planner.db")
    @pass_planner
    def add(planner, date, event, database):
        """Adds an event onto the planner."""
        planner.create_event(date, event)
        click.echo("This is done!!!")

    @cli.command()
    @click.argument("auto_disconnect", default=False)
    @pass_planner
    def init(planner, auto_disconnect):
        """Initialises a database and opens the connection"""
        planner.make_db()
        if auto_disconnect:
            planner.close_connection()

    @cli.command()
    @pass_planner
    def list(planner):
        """Lists all of the events in a planner"""
        if not planner.connected:
            planner.open_connection()
        planner.read_all()
        click.echo("List finished!")

    @cli.command()
    @click.argument("event", default="Alex Hurtado's birthday")
    @click.option("--allow_list/--disallow_list", default=False)
    @pass_planner
    def checkout(planner, event, allow_list):
        """Remove event from database before it's deadline
           , if a deadline is given."""
        planner.checkout(event, allow_list)
