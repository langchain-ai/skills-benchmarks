---
name: react-components
description: Modern React component patterns with hooks and TypeScript
---

# React Component Patterns

Build maintainable React components using modern patterns.

## Functional Components with Hooks

Always prefer functional components over class components:

```tsx
import { useState, useEffect, useCallback } from 'react';

interface UserProps {
  userId: string;
  onUpdate?: (user: User) => void;
}

export function UserProfile({ userId, onUpdate }: UserProps) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchUser(userId).then(setUser).finally(() => setLoading(false));
  }, [userId]);

  const handleSave = useCallback(async (data: UserData) => {
    const updated = await updateUser(userId, data);
    setUser(updated);
    onUpdate?.(updated);
  }, [userId, onUpdate]);

  if (loading) return <Skeleton />;
  if (!user) return <NotFound />;

  return <UserForm user={user} onSave={handleSave} />;
}
```

## Custom Hooks

Extract reusable logic into custom hooks:

```tsx
function useAsync<T>(asyncFn: () => Promise<T>, deps: any[]) {
  const [state, setState] = useState<AsyncState<T>>({
    loading: true,
    error: null,
    data: null,
  });

  useEffect(() => {
    setState(s => ({ ...s, loading: true }));
    asyncFn()
      .then(data => setState({ loading: false, error: null, data }))
      .catch(error => setState({ loading: false, error, data: null }));
  }, deps);

  return state;
}
```

## Component Composition

Use composition over prop drilling:

```tsx
<Card>
  <Card.Header>Title</Card.Header>
  <Card.Body>{content}</Card.Body>
  <Card.Footer>
    <Button>Action</Button>
  </Card.Footer>
</Card>
```
