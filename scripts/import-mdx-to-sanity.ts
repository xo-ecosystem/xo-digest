import fs from 'fs'
import path from 'path'
import sanityClient from '@sanity/client'
import { v4 as uuidv4 } from 'uuid'

const client = sanityClient({
  projectId: 'your_project_id', // replace
  dataset: 'production',
  useCdn: false,
  token: process.env.SANITY_TOKEN,
  apiVersion: '2023-07-09',
})

const VAULT_DIR = path.resolve(__dirname, '../../vault/daily')

async function importMDX() {
  const files = fs.readdirSync(VAULT_DIR).filter(f => f.endsWith('.mdx'))

  for (const file of files) {
    const fullPath = path.join(VAULT_DIR, file)
    const content = fs.readFileSync(fullPath, 'utf-8')

    const slug = path.basename(file, '.mdx')
    const doc = {
      _id: `digestEntry-${slug}`,
      _type: 'digestEntry',
      title: slug.replace(/-/g, ' '),
      slug: { _type: 'slug', current: slug },
      body: [
        {
          _type: 'block',
          style: 'normal',
          children: [{ _type: 'span', text: content }]
        }
      ],
      publishedAt: new Date().toISOString(),
    }

    console.log(`⏳ Importing ${slug}...`)
    await client.createOrReplace(doc)
    console.log(`✅ Imported ${slug}`)
  }
}

importMDX().catch(err => {
  console.error('❌ Error importing MDX:', err)
})
