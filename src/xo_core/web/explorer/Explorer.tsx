import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';

interface ExplorerData {
  content: string;
  title?: string;
  metadata?: any;
}

export const Explorer: React.FC = () => {
  const { slug } = useParams<{ slug: string }>();
  const [data, setData] = useState<ExplorerData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!slug) {
      setError('No slug provided');
      setLoading(false);
      return;
    }

    // Try to fetch from vault preview endpoint
    fetch(`/api/vault/preview/${slug}`)
      .then(res => {
        if (!res.ok) {
          throw new Error(`HTTP ${res.status}: ${res.statusText}`);
        }
        return res.json();
      })
      .then((data) => {
        setData(data);
        setLoading(false);
      })
      .catch((err) => {
        console.warn('Failed to load from vault preview:', err);
        // Fallback: try to load as static HTML
        return fetch(`/vault/preview/${slug}.html`);
      })
      .then((res) => {
        if (res && res.ok) {
          return res.text();
        }
        throw new Error('Not found');
      })
      .then((html) => {
        setData({ content: html });
        setLoading(false);
      })
      .catch((err) => {
        setError(`Failed to load content: ${err.message}`);
        setLoading(false);
      });
  }, [slug]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading explorer content...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center max-w-md mx-auto p-6">
          <div className="text-red-500 text-6xl mb-4">⚠️</div>
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Content Not Found</h1>
          <p className="text-gray-600 mb-4">{error}</p>
          <p className="text-sm text-gray-500">
            Slug: <code className="bg-gray-100 px-2 py-1 rounded">{slug}</code>
          </p>
          <button 
            onClick={() => window.history.back()}
            className="mt-4 bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded"
          >
            Go Back
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <p className="text-gray-600">No content available</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-white rounded-lg shadow-sm p-8">
          {data.title && (
            <h1 className="text-3xl font-bold text-gray-900 mb-6">{data.title}</h1>
          )}
          
          {data.metadata && (
            <div className="bg-gray-100 p-4 rounded-lg mb-6">
              <h2 className="text-lg font-semibold mb-2">Metadata</h2>
              <pre className="text-sm text-gray-700 overflow-x-auto">
                {JSON.stringify(data.metadata, null, 2)}
              </pre>
            </div>
          )}
          
          <div 
            className="prose prose-lg max-w-none"
            dangerouslySetInnerHTML={{ __html: data.content }}
          />
        </div>
      </div>
    </div>
  );
}; 