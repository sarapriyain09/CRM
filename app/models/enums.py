import enum


class PlatformType(str, enum.Enum):
    tiktok = "tiktok"
    instagram = "instagram"
    youtube = "youtube"
    linkedin = "linkedin"
    x = "x"
    facebook = "facebook"
    reddit = "reddit"
    other = "other"


class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    proposal = "proposal"
    won = "won"
    lost = "lost"
    nurture = "nurture"


class LeadIntent(str, enum.Enum):
    student = "student"
    small_business = "small_business"
    ecommerce = "ecommerce"
    internal_tool = "internal_tool"
    agency_client = "agency_client"
    unknown = "unknown"


class PostStatus(str, enum.Enum):
    draft = "draft"
    approved = "approved"
    scheduled = "scheduled"
    published = "published"
    failed = "failed"


class HandoffTarget(str, enum.Enum):
    codlearn = "codlearn"
    splendid = "splendid"
