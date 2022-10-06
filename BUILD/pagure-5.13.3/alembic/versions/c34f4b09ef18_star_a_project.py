"""star_a_project

Revision ID: c34f4b09ef18
Revises: 8a5d68f74beb
Create Date: 2017-07-07 00:08:18.257075

"""

# revision identifiers, used by Alembic.
revision = 'c34f4b09ef18'
down_revision = '8a5d68f74beb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ''' Add a new table to store data about who starred which project '''
    op.create_table(
        'stargazers',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column(
            'project_id',
            sa.Integer,
            sa.ForeignKey(
                'projects.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
            index=True,
        ),
        sa.Column(
            'user_id',
            sa.Integer,
            sa.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'),
            nullable=False,
        )
    )

    op.create_unique_constraint(
        constraint_name='uq_stargazers_project_id_user_id_key',
        table_name='stargazers',
        columns=['project_id', 'user_id']
    )


def downgrade():
    ''' Remove the stargazers table from the database '''
    op.drop_constraint(
        constraint_name='uq_stargazers_project_id_user_id_key',
        table_name='stargazers'
    )
    op.drop_table('stargazers')
