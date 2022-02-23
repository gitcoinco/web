import datetime

from dashboard.tests.factories import ProfileFactory
from grants.tests.factories import CLRMatchFactory, GrantFactory, GrantPayoutFactory, GrantCLRFactory, GrantCLRCalculationFactory, GrantTypeFactory

grant_type = GrantTypeFactory()
profile = ProfileFactory()
network='mainnet'

GrantFactory(active=True, network=network, grant_type=grant_type, last_update=datetime.datetime.now(), admin_profile=profile)