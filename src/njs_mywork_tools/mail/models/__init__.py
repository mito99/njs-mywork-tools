"""
Mail models package for mail data structures
""" 

from .entities import (AttachmentEntity, ContactEntity, MailMessageEntity,
                       RecipientEntity, RecipientType, SenderEntity)

__all__ = [
    "MailMessageEntity", 
    "RecipientEntity", 
    "AttachmentEntity", 
    "ContactEntity", 
    "SenderEntity",
    "RecipientType",
]
