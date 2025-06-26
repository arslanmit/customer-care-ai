# Import all action classes from individual files
from .action_ask_how_can_i_help import ActionAskHowCanIHelp
from .action_ask_order_number import ActionAskOrderNumber
from .action_check_order_status import ActionCheckOrderStatus
from .action_contact_support import ActionContactSupport
from .action_default_fallback import ActionDefaultFallback
from .action_handoff_to_human import ActionHandoffToHuman
from .action_provide_order_status import ActionProvideOrderStatus
from .action_provide_return_policy import ActionProvideReturnPolicy
from .action_return_item import ActionReturnItem
from .action_tell_date import ActionTellDate
from .action_tell_joke import ActionTellJoke
from .action_tell_time import ActionTellTime

# Import slot extraction actions
from .action_extract_slots import (
    ActionExtractOrderNumber,
    ActionExtractProductId,
    ActionExtractEmail,
    ActionExtractPhoneNumber,
    ActionExtractDate,
    ActionExtractTime,
    ActionExtractLanguage,
    ActionExtractFirstName,
    ActionExtractLastName,
    ActionExtractComplaintType,
    ActionExtractComplaintDetails,
    ActionExtractCustomerEmail
)

# Also import from actions.py if it contains additional actions
from .actions import (
    ActionGetTime,
    ActionGetDate,
    ActionTellDateTime,
    ActionIncrementFallbackCount as CoreIncrementFallbackCount,
    ActionSetLanguage,
    ActionTrackOrder,
    ActionLogComplaint,
    ActionRecommendProduct,
    ActionEscalateToHuman
)

__all__ = [
    # Original actions
    'ActionAskHowCanIHelp',
    'ActionAskOrderNumber',
    'ActionCheckOrderStatus',
    'ActionContactSupport',
    'ActionDefaultFallback',
    'ActionHandoffToHuman',
    'ActionProvideOrderStatus',
    'ActionProvideReturnPolicy',
    'ActionReturnItem',
    'ActionTellDate',
    'ActionTellJoke',
    'ActionTellTime',
    
    # Slot extraction actions
    'ActionExtractOrderNumber',
    'ActionExtractProductId',
    'ActionExtractEmail',
    'ActionExtractPhoneNumber',
    'ActionExtractDate',
    'ActionExtractTime',
    'ActionExtractLanguage',
    'ActionExtractFirstName',
    'ActionExtractLastName',
    'ActionExtractComplaintType',
    'ActionExtractComplaintDetails',
    'ActionExtractCustomerEmail',
    
    # Core actions
    'ActionGetTime',
    'ActionGetDate',
    'ActionTellDateTime',
    'CoreIncrementFallbackCount',
    'ActionSetLanguage',
    'ActionTrackOrder',
    'ActionLogComplaint',
    'ActionRecommendProduct',
    'ActionEscalateToHuman'
]