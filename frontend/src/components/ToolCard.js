import React from 'react';
import { Link } from 'react-router-dom';

function ToolCard({ tool }) {
  const truncatedDescription = tool.description
    ? tool.description.length > 120
      ? `${tool.description.substring(0, 120)}...`
      : tool.description
    : '';

  return (
    <div className="bg-white rounded-lg shadow-md p-4 h-full flex flex-col hover:shadow-xl transition-shadow">
      <Link
        to={`/tool/${tool.id}`}
        className="block mb-3 group"
        aria-label={`View details for ${tool.name}`}
      >
        <img
          src={tool.image_url || '/placeholder.png'}
          alt={tool.name}
          className="w-full h-48 object-cover rounded-lg transition-transform duration-150 group-hover:scale-[1.02]"
          onError={(e) => {
            e.target.src = '/placeholder.png';
          }}
        />
      </Link>
      <h3 className="font-bold text-lg mb-2 text-gray-900">{tool.name}</h3>
      {truncatedDescription && (
        <p className="text-gray-600 text-sm mb-3 flex-grow">{truncatedDescription}</p>
      )}
      <div className="flex gap-2 flex-wrap mb-4">
        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
          {tool.category}
        </span>
        <span
          className={`px-2 py-1 rounded-full text-xs ${
            tool.price_type === 'Free'
              ? 'bg-green-100 text-green-800'
              : tool.price_type === 'Paid'
              ? 'bg-red-100 text-red-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}
        >
          {tool.price_type}
        </span>
      </div>
      <Link
        to={`/tool/${tool.id}`}
        className="mt-auto inline-flex items-center justify-center rounded-md bg-blue-600 px-3 py-1.5 text-sm font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
      >
        Details
      </Link>
    </div>
  );
}

export default ToolCard;