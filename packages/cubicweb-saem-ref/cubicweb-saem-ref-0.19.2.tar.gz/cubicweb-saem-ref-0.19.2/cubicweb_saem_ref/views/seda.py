# copyright 2015 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.
"""cubicweb-saem-ref views related to SEDA"""

from cubicweb.web.views import uicfg

from cubicweb_seda.views import (
    CONTENT_ETYPE,
    archivetransfer,
    archiveunit,
    rtags_from_rtype_role_targets,
    simplified
)


afs = uicfg.autoform_section
pvs = uicfg.primaryview_section

# we want only simplified_profile, so its default is set to true and it only has to be hidden
afs.tag_attribute(('SEDAArchiveTransfer', 'simplified_profile'), 'main', 'hidden')
# also hide transferring and archival agency
for rtype in ('seda_transferring_agency', 'seda_archival_agency'):
    afs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'main', 'hidden')
    pvs.tag_subject_of(('SEDAArchiveTransfer', rtype, '*'), 'hidden')

pvs.tag_object_of(('*', 'use_profile', '*'), 'hidden')
afs.tag_object_of(('*', 'use_profile', '*'), 'main', 'hidden')

pvs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'hidden')
afs.tag_attribute(('SEDABinaryDataObject', 'filename'), 'main', 'hidden')


archivetransfer.ArchiveTransferTabbedPrimaryView.tabs.append('saem.lifecycle_tab')


# Hide "identifiant pour le service versant" which should be automatically
# filled.
class SimplifiedContentMainView(archiveunit.SimplifiedContentMainView):

    rtype_role_targets = archiveunit.SimplifiedContentMainView.rtype_role_targets[:]
    rtype_role_targets.remove(
        ('seda_transferring_agency_archive_unit_identifier', 'object', None)
    )
    rsection, display_ctrl = rtags_from_rtype_role_targets(CONTENT_ETYPE, rtype_role_targets)


simplified.simplified_afs.tag_object_of(
    ('*', 'seda_transferring_agency_archive_unit_identifier', CONTENT_ETYPE),
    'main', 'hidden',
)


def registration_callback(vreg):
    vreg.register_all(globals().values(), __name__, [SimplifiedContentMainView])
    vreg.register_and_replace(SimplifiedContentMainView, archiveunit.SimplifiedContentMainView)
