import React, { useState } from 'react';
import {
  ZoomIn,
  ZoomOut,
  RotateCcw,
  GitBranch,
  Info,
  CheckCircle2,
} from 'lucide-react';
import { Button } from './ui';

export interface TreeNodeData {
  node_id: number;
  depth: number;
  is_leaf: boolean;
  samples: number;
  impurity: number;
  impurity_name?: string;
  value?: number[];
  class: string;
  feature?: string;
  threshold?: number;
  condition?: string;
  left?: TreeNodeData;
  right?: TreeNodeData;
}

export const InteractiveDecisionTree: React.FC<{
  treeData: TreeNodeData;
}> = ({ treeData }) => {
  const [scale, setScale] = useState<number>(1);
  const [selectedNode, setSelectedNode] = useState<TreeNodeData | null>(null);

  const handleZoomIn = () => setScale((s) => Math.min(1.8, s + 0.15));
  const handleZoomOut = () => setScale((s) => Math.max(0.6, s - 0.15));
  const handleReset = () => {
    setScale(1);
    setSelectedNode(null);
  };

  // Node width and height
  const NODE_W = 190;
  const NODE_H = 95;

  // Flatten tree for SVG rendering with computed coordinates
  const renderSubtree = (
    node: TreeNodeData,
    x: number,
    y: number,
    levelGap: number
  ): React.ReactNode => {
    const isSelected = selectedNode?.node_id === node.node_id;
    const isLeaf = node.is_leaf;
    const borderCol = isSelected ? 'var(--acd)' : 'var(--bd)';
    const headerBg = isLeaf ? 'var(--soft)' : '#f5f0e4';

    return (
      <g key={node.node_id}>
        {/* Connectors to children */}
        {node.left && (
          <>
            <line
              x1={x + NODE_W / 2}
              y1={y + NODE_H}
              x2={x - levelGap + NODE_W / 2}
              y2={y + 140}
              stroke="var(--bd)"
              strokeWidth="1.5"
            />
            <rect
              x={(x + x - levelGap + NODE_W) / 2 - 24}
              y={y + NODE_H + 12}
              width="48"
              height="18"
              rx="4"
              fill="#fff"
              stroke="var(--bd)"
            />
            <text
              x={(x + x - levelGap + NODE_W) / 2}
              y={y + NODE_H + 25}
              textAnchor="middle"
              fontSize="9"
              fontWeight="600"
              fill="var(--acd)"
            >
              True (≤)
            </text>
            {renderSubtree(node.left, x - levelGap, y + 140, levelGap / 2)}
          </>
        )}

        {node.right && (
          <>
            <line
              x1={x + NODE_W / 2}
              y1={y + NODE_H}
              x2={x + levelGap + NODE_W / 2}
              y2={y + 140}
              stroke="var(--bd)"
              strokeWidth="1.5"
            />
            <rect
              x={(x + x + levelGap + NODE_W) / 2 - 24}
              y={y + NODE_H + 12}
              width="48"
              height="18"
              rx="4"
              fill="#fff"
              stroke="var(--bd)"
            />
            <text
              x={(x + x + levelGap + NODE_W) / 2}
              y={y + NODE_H + 25}
              textAnchor="middle"
              fontSize="9"
              fontWeight="600"
              fill="var(--err)"
            >
              False (&gt;)
            </text>
            {renderSubtree(node.right, x + levelGap, y + 140, levelGap / 2)}
          </>
        )}

        {/* Node Box */}
        <g
          transform={`translate(${x}, ${y})`}
          onClick={() => setSelectedNode(node)}
          style={{ cursor: 'pointer' }}
        >
          <rect
            width={NODE_W}
            height={NODE_H}
            rx="6"
            fill="#fff"
            stroke={borderCol}
            strokeWidth={isSelected ? 2.5 : 1.2}
            filter="drop-shadow(0px 2px 4px rgba(0,0,0,0.05))"
          />

          {/* Node Header */}
          <rect width={NODE_W} height="26" rx="6" fill={headerBg} />
          <rect y="20" width={NODE_W} height="6" fill={headerBg} />
          <text x="10" y="17" fontSize="11" fontWeight="bold" fill="var(--tx)">
            {isLeaf ? `🍃 Leaf (Class: ${node.class.split(' ')[0]})` : `🌿 Split Node #${node.node_id}`}
          </text>

          {/* Condition or Prediction */}
          <text x="10" y="44" fontSize="11" fontWeight="600" fill="var(--tx)">
            {node.condition || `Predict: ${node.class}`}
          </text>

          {/* Metrics */}
          <text x="10" y="62" fontSize="10" fill="var(--mu)">
            {node.impurity_name || 'Gini'}: {node.impurity.toFixed(3)} · Samples: {node.samples.toLocaleString()}
          </text>

          {/* Distribution Mini-Bar */}
          <rect x="10" y="74" width={NODE_W - 20} height="6" rx="3" fill="var(--bd)" />
          {node.value && (
            <rect
              x="10"
              y="74"
              width={Math.min(NODE_W - 20, ((node.value[0] || 0) / node.samples) * (NODE_W - 20))}
              height="6"
              rx="3"
              fill="var(--acd)"
            />
          )}
        </g>
      </g>
    );
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
      {/* Controls Bar */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          backgroundColor: 'var(--card)',
          border: '1px solid var(--bd)',
          borderRadius: '8px',
          padding: '8px 14px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <GitBranch size={16} color="var(--acd)" />
          <span style={{ fontSize: '13px', fontWeight: 600, color: 'var(--tx)' }}>
            Interactive Decision Tree Hierarchy
          </span>
        </div>
        <div style={{ display: 'flex', gap: '6px' }}>
          <Button size="sm" onClick={handleZoomIn} icon={<ZoomIn size={13} />}>
            Zoom In
          </Button>
          <Button size="sm" onClick={handleZoomOut} icon={<ZoomOut size={13} />}>
            Zoom Out
          </Button>
          <Button size="sm" onClick={handleReset} icon={<RotateCcw size={13} />}>
            Reset
          </Button>
        </div>
      </div>

      {/* SVG Canvas Area */}
      <div
        style={{
          width: '100%',
          height: '420px',
          overflow: 'auto',
          backgroundColor: '#faf7f2',
          border: '1px solid var(--bd)',
          borderRadius: '8px',
          padding: '20px',
        }}
      >
        <div style={{ transform: `scale(${scale})`, transformOrigin: 'top center', transition: 'transform 0.2s ease' }}>
          <svg width="860" height="380" viewBox="0 0 860 380" style={{ display: 'block', margin: '0 auto' }}>
            {renderSubtree(treeData, 335, 10, 220)}
          </svg>
        </div>
      </div>

      {/* Selected Node Details */}
      {selectedNode && (
        <div
          style={{
            backgroundColor: 'var(--card)',
            border: '1px solid var(--bd)',
            borderRadius: '8px',
            padding: '14px 18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '12.5px',
          }}
        >
          <div>
            <strong>Node #{selectedNode.node_id} Selected:</strong>{' '}
            <span>{selectedNode.condition || `Terminal Leaf → Class ${selectedNode.class}`}</span>
          </div>
          <div style={{ display: 'flex', gap: '14px', color: 'var(--mu)' }}>
            <span>Samples: {selectedNode.samples.toLocaleString()}</span>
            <span>Impurity: {selectedNode.impurity.toFixed(3)}</span>
            <span>Depth: {selectedNode.depth}</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default InteractiveDecisionTree;

