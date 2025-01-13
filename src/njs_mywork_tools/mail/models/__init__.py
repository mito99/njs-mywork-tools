"""
Mail models package for mail data structures
""" 

from .entities import AttachmentEntity, MailMessageEntity, RecipientEntity

__all__ = ["MailMessageEntity", "RecipientEntity", "AttachmentEntity"]
