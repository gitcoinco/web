# -*- coding: utf-8 -*-
'''
    Copyright (C) 2021 Gitcoin Core

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU Affero General Public License as published
    by the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
    GNU Affero General Public License for more details.

    You should have received a copy of the GNU Affero General Public License
    along with this program. If not, see <http://www.gnu.org/licenses/>.

'''

from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

quickstart = {
    'good_issue_types': [
        {
            'title': 'Performance',
            'description': 'Performance improvement.',
            'img': static('v2/images/quickstart-icons/performance-icon.svg'),
            'good_first_bounty': True
        },
        {
            'title': 'Security',
            'description': 'Find vulnerabilities',
            'img': static('v2/images/quickstart-icons/security-icon.svg'),
            'good_first_bounty': True
        },
        {
            'title': 'Testing',
            'description': 'Test your code',
            'img': static('v2/images/quickstart-icons/testing-icon.svg'),
            'good_first_bounty': True
        },
        {
            'title': 'New Product or Feature',
            'description': 'Build new product ideas or new features',
            'img': static('v2/images/quickstart-icons/newproduct-icon.svg')
        },
        {
            'title': 'Feature Improvement',
            'description': 'Iterate on the next set of features',
            'img': static('v2/images/quickstart-icons/feature-icon.svg')
        },
        {
            'title': 'Bug Fix',
            'description': 'Find and fix bugs in your product',
            'img': static('v2/images/quickstart-icons/bug-icon.svg')
        },
        {
            'title': 'Tech Upgrade',
            'description': 'Framework, migration, batches',
            'img': static('v2/images/quickstart-icons/upgrade-icon.svg')
        },
        {
            'title': 'Design',
            'description': 'Architecture, flows, wireframes, designs',
            'img': static('v2/images/quickstart-icons/design-icon.svg')
        },
        {
            'title': 'Code Review',
            'description': 'Get help reviewing code',
            'img': static('v2/images/quickstart-icons/review-icon.svg')
        },
        {
            'title': 'Documentation',
            'description': 'Product documentation, set up instructions',
            'img': static('v2/images/quickstart-icons/documentation-icon.svg')
        },
        {
            'title': 'Other',
            'description': 'Ideas, discussions, contests, consulting',
            'img': static('v2/images/quickstart-icons/other-icon.svg')
        }
    ],
    'bad_issue_types': [
        {
            'title': _('Core Architecture'),
            'description': _('Building your app from ground up.'),
            'img': static('v2/images/quickstart-icons/architecture-icon.svg')
        },
        {
            'title': _('Requires Awarness of Product Market fit'),
            'description': _('unless there is well documented materials.'),
            'img': static('v2/images/quickstart-icons/awarness-icon.svg')
        },
        {
            'title': _('Requires Privileged Access'),
            'description': _('SSH access, prod private API key, etc.'),
            'img': static('v2/images/quickstart-icons/access-icon.svg')
        }
    ],
    'bounty_tips': [
        {
            'title': _('Price Correctly'),
            'description': _('Make sure the <strong>Pricing</strong> of your bounty matches the work requirement.'),
            'img': static('v2/images/quickstart-icons/price-icon.svg')
        },
        {
            'title': _('Start Small'),
            'description': _('Focus on verifiable tasks and small tasks.'),
            'img': static('v2/images/quickstart-icons/startsmall-icon.svg')
        },
        {
            'title': _('Set Clear Acceptance Criteria'),
            'description': _('Have clear checklist on the <strong>Bounty Details</strong> on the definition of done.'),
            'img': static('v2/images/quickstart-icons/acceptance-icon.svg')
        },
                {
            'title': _('Focus on Iteration'),
            'description': _('Keep budget in your back pocket and keep a tight iteration loop. Leave no room for error.'),
            'img': static('v2/images/quickstart-icons/iteration-icon.svg')
        },
        {
            'title': _('Set A Reasonable Time Frame'),
            'description': _('Put a reasonable time frame on the <strong>Time Commitment</strong> field.'),
            'img': static('v2/images/quickstart-icons/timeframe-icon.svg')
        },
        {
            'title': _('Documentation is Key'),
            'description': _('Clear readmes and contributing guidelines on your GitHub repo are important.'),
            'img': static('v2/images/quickstart-icons/doc-icon.svg')
        }
    ],
    'title': _('Quickstart'),
}
