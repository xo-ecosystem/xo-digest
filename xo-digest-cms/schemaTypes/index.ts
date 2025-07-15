import blockContent from './blockContent'
import category from './category'
import post from './post'
import author from './author'
import digestEntry from './digestEntry'
import mediaAttachment from './mediaAttachment'
import syncMetadata from './syncMetadata'

export const schemaTypes = [
  post,
  author,
  category,
  blockContent,
  digestEntry,
  mediaAttachment,
  syncMetadata,
  // upcoming XO schema extensions:
  // digestEntry, mediaAttachment, syncMetadata
]
