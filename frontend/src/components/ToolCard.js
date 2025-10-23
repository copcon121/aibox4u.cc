import React from 'react';
import { Link } from 'react-router-dom';

function ToolCard({ tool }) {
  return (
    <Link to={`/tool/${tool.id}`} className="block hover:shadow-xl transition-shadow">
      <div className="bg-white rounded-lg shadow-md p-4 h-full flex flex-col">
        <img 
          src={tool.image_url || '/placeholder.png'} 
          alt={tool.name} 
          className="w-full h-48 object-cover rounded-lg mb-3"
          onError={(e) => {
            e.target.src = '/placeholder.png';
          }}
        />
        <h3 className="font-bold text-lg mb-2 text-gray-900">{tool.name}</h3>
        <p className="text-gray-600 text-sm mb-3 flex-grow">
          {tool.description?.substring(0, 120)}...
        </p>
        <div className="flex gap-2 flex-wrap">
          <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded-full text-xs">
            {tool.category}
          </span>
          <span className={`px-2 py-1 rounded-full text-xs ${
            tool.price_type === 'Free' ? 'bg-green-100 text-green-800' :
            tool.price_type === 'Paid' ? 'bg-red-100 text-red-800' :
            'bg-yellow-100 text-yellow-800'
          }`}>
            {tool.price_type}
          </span>
        </div>
      </div>
    </Link>
  );
}

export default ToolCard;