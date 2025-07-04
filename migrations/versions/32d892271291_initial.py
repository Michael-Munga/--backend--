"""initial

Revision ID: 32d892271291
Revises: 
Create Date: 2025-07-02 10:21:36.429920

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32d892271291'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('departments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=225), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_departments')),
    sa.UniqueConstraint('name', name=op.f('uq_departments_name'))
    )
    op.create_table('job_titles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_job_titles')),
    sa.UniqueConstraint('title', name=op.f('uq_job_titles_title'))
    )
    op.create_table('user_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=50), nullable=False),
    sa.Column('description', sa.String(length=225), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_user_types')),
    sa.UniqueConstraint('name', name=op.f('uq_user_types_name'))
    )
    op.create_table('employees',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('first_name', sa.String(), nullable=False),
    sa.Column('last_name', sa.String(), nullable=False),
    sa.Column('email', sa.String(length=100), nullable=False),
    sa.Column('phone', sa.String(length=100), nullable=True),
    sa.Column('hire_date', sa.DateTime(), nullable=True),
    sa.Column('password_hash', sa.String(length=128), nullable=False),
    sa.Column('department_id', sa.Integer(), nullable=True),
    sa.Column('user_type_id', sa.Integer(), nullable=True),
    sa.Column('job_title_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['department_id'], ['departments.id'], name=op.f('fk_employees_department_id_departments')),
    sa.ForeignKeyConstraint(['job_title_id'], ['job_titles.id'], name=op.f('fk_employees_job_title_id_job_titles')),
    sa.ForeignKeyConstraint(['user_type_id'], ['user_types.id'], name=op.f('fk_employees_user_type_id_user_types')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_employees')),
    sa.UniqueConstraint('email', name=op.f('uq_employees_email')),
    sa.UniqueConstraint('phone', name=op.f('uq_employees_phone'))
    )
    op.create_table('attendances',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('check_in_time', sa.Time(), nullable=True),
    sa.Column('check_out_time', sa.Time(), nullable=True),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], name=op.f('fk_attendances_employee_id_employees')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_attendances'))
    )
    op.create_table('performance_reviews',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('review_date', sa.DateTime(), nullable=True),
    sa.Column('reviewer', sa.String(length=50), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.Column('rating', sa.Integer(), nullable=True),
    sa.Column('employee_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['employee_id'], ['employees.id'], name=op.f('fk_performance_reviews_employee_id_employees')),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_performance_reviews'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('performance_reviews')
    op.drop_table('attendances')
    op.drop_table('employees')
    op.drop_table('user_types')
    op.drop_table('job_titles')
    op.drop_table('departments')
    # ### end Alembic commands ###
