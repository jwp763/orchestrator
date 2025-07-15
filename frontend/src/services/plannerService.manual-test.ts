/**
 * Manual test script for PlannerService
 * Run in browser console after importing
 */
import { getPlannerService } from './plannerService';

export async function testPlannerService() {
  const service = getPlannerService();
  
  console.log('Testing PlannerService...');
  
  // Test 1: Get providers
  console.log('\n1. Testing getProviders():');
  try {
    const providersResult = await service.getProviders();
    console.log('Providers result:', providersResult);
    if (providersResult.success) {
      console.log('Available providers:', providersResult.data?.providers.map(p => p.name));
    } else {
      console.error('Failed to get providers:', providersResult.error);
    }
  } catch (error) {
    console.error('Error getting providers:', error);
  }
  
  // Test 2: Get default config
  console.log('\n2. Testing getDefaultConfig():');
  try {
    const configResult = await service.getDefaultConfig();
    console.log('Config result:', configResult);
    if (configResult.success) {
      console.log('Default provider:', configResult.data?.default_config.provider);
    } else {
      console.error('Failed to get config:', configResult.error);
    }
  } catch (error) {
    console.error('Error getting config:', error);
  }
  
  // Test 3: Get cache stats
  console.log('\n3. Testing getCacheStats():');
  try {
    const statsResult = await service.getCacheStats();
    console.log('Cache stats result:', statsResult);
    if (statsResult.success) {
      console.log('Cache hit rate:', statsResult.data?.hit_rate);
    } else {
      console.error('Failed to get cache stats:', statsResult.error);
    }
  } catch (error) {
    console.error('Error getting cache stats:', error);
  }
  
  // Test 4: Generate plan (only if backend is properly configured)
  console.log('\n4. Testing generatePlan():');
  try {
    const planResult = await service.generatePlan({
      idea: 'Build a simple todo list application with user authentication',
      config: {
        provider: 'openai',
        create_milestones: true,
        max_milestones: 3,
        max_retries: 2,
      },
    });
    console.log('Plan generation result:', planResult);
    if (planResult.success) {
      console.log('Generated project:', planResult.data?.project?.name);
      console.log('Generated tasks:', planResult.data?.tasks.length);
    } else {
      console.error('Failed to generate plan:', planResult.error);
    }
  } catch (error) {
    console.error('Error generating plan:', error);
  }
  
  console.log('\nPlannerService test complete!');
}

// Export for use in browser console
(window as any).testPlannerService = testPlannerService;