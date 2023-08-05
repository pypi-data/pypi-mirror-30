"""SQLAlchemy-powered model definition for roles."""
# pylint: disable = super-on-old-class

from lxml import etree
from sqlalchemy import Column, ForeignKey, types
from sqlalchemy.schema import PrimaryKeyConstraint, UniqueConstraint
from sqlalchemy.schema import ForeignKeyConstraint
from sqlalchemy.orm import relationship

from ..lib.utils import normalize_spaces, wrap
from . import Base, DBSession, LABEL_LEN, DESCRIPTION_LEN


XML_NS = '{http://www.w3.org/XML/1998/namespace}'


# =============================================================================
class Role(Base):
    """SQLAlchemy-powered role model."""

    __tablename__ = 'role'
    __table_args__ = (
        PrimaryKeyConstraint('project_id', 'role_id'),
        UniqueConstraint('role_id'), UniqueConstraint('project_id', 'label'),
        {'mysql_engine': 'InnoDB'})

    project_id = Column(
        types.Integer, ForeignKey('project.project_id', ondelete='CASCADE'))
    role_id = Column(types.Integer, autoincrement=True)
    label = Column(types.String(LABEL_LEN), nullable=False)
    description = Column(types.String(DESCRIPTION_LEN))

    users = relationship('RoleUser', cascade='all, delete')

    # -------------------------------------------------------------------------
    def __init__(self, project_id, label, description=None):
        """Constructor method."""
        super(Role, self).__init__()
        self.project_id = project_id
        self.label = normalize_spaces(label, LABEL_LEN)
        self.description = \
            normalize_spaces(description, DESCRIPTION_LEN) or None

    # -------------------------------------------------------------------------
    @classmethod
    def load(cls, project_id, role_elt):
        """Load a user from a XML element.

        :param project_id: (integer)
            Project ID.
        :param role_elt: (:class:`lxml.etree.Element` instance)
            Role XML element.
        :return: (integer)
            Role ID.
        """
        role = cls(project_id, role_elt.findtext('label'),
                   role_elt.findtext('description'))
        DBSession.add(role)
        DBSession.commit()

        return role.role_id

    # -------------------------------------------------------------------------
    def xml(self):
        """Serialize a role to a XML representation.

        :return: (:class:`lxml.etree.Element`)
        """
        role_elt = etree.Element('role')
        role_elt.set(
            '%sid' % XML_NS, 'rol%d.%d' % (self.project_id, self.role_id))
        etree.SubElement(role_elt, 'label').text = self.label
        if self.description:
            etree.SubElement(role_elt, 'description').text = \
                wrap(self.description, width=66, indent=12)

        return role_elt


# =============================================================================
class RoleUser(Base):
    """SQLAlchemy-powered association table between ``Role`` and
    ``User``."""
    # pylint: disable = too-few-public-methods

    __tablename__ = 'role_user'
    __table_args__ = (
        ForeignKeyConstraint(
            ['project_id', 'role_id'],
            ['role.project_id', 'role.role_id'], ondelete='CASCADE'),
        {'mysql_engine': 'InnoDB'})
    project_id = Column(types.Integer, primary_key=True)
    role_id = Column(types.Integer, primary_key=True)
    user_id = Column(types.Integer, primary_key=True)

    # -------------------------------------------------------------------------
    def __init__(self, project_id, role_id, user_id):
        """Constructor method."""
        super(RoleUser, self).__init__()
        self.project_id = project_id
        self.role_id = role_id
        self.user_id = user_id
