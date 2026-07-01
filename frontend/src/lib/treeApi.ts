import { apiClient } from '@/api/axios';
import type { TreeNode } from '@/types/skill';

export async function fetchTreeRoot(): Promise<TreeNode[]> {
  try {
    const { data } = await apiClient.get('/api/skills');
    // If backend returns a paginated list of skills:
    const skills = data?.data?.items || data?.data || [];
    
    return skills.map((skill: any) => ({
      id: skill.id,
      title: skill.title || skill.name,
      type: 'skill',
      depth: 0,
      progress: skill.progress || 0,
      childrenCount: skill.totalTopics || 0,
      hasChildren: (skill.totalTopics || 0) > 0,
      loaded: false,
      expanded: false,
      checkState: skill.progress === 100 ? 'checked' : (skill.progress > 0 ? 'indeterminate' : 'unchecked'),
    }));
  } catch (err) {
    console.error('Failed to load tree root', err);
    throw err;
  }
}

export async function fetchTreeChildren(parentId: string): Promise<TreeNode[]> {
  try {
    // Determine if parent is a skill or a topic to construct the correct URL
    // Actually, backend has `/api/topics` which we can filter by skill_id
    // or `/api/topics/{id}/descendants` or `/api/topics/{id}/children`. 
    // We'll try hitting `/api/topics` with `parent_id` parameter or `skill_id`.
    
    const { data } = await apiClient.get('/api/topics', {
      params: { 
        parent_id: parentId, // Or skill_id if the root is a skill and backend supports it
        limit: 100
      }
    });

    const children = data?.data?.items || data?.data || [];
    
    return children.map((child: any) => ({
      id: child.id,
      title: child.title,
      type: child.type || 'topic',
      depth: (child.depth || 0) + 1,
      progress: child.progress || 0,
      childrenCount: child.children_count || 0,
      hasChildren: (child.children_count || 0) > 0,
      loaded: false,
      expanded: false,
      parentId,
      checkState: child.is_completed ? 'checked' : (child.progress > 0 ? 'indeterminate' : 'unchecked'),
    }));
  } catch (err) {
    console.error('Failed to fetch tree children', err);
    throw err;
  }
}
