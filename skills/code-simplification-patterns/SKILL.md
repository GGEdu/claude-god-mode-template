---
name: code-simplification-patterns
description: >-
  Patterns for simplifying working code to reduce cognitive load.
  Early returns, async/await, extract nested logic, eliminate redundant state,
  simplify booleans, flatten collections. Behavior preservation is non-negotiable.
impact: low
---

# Code Simplification Patterns

Reference patterns for reducing cognitive load in working code. Apply after features are working and tested — never during active development.

**Core Constraint:** Behavior preservation is non-negotiable. If unsure whether a simplification changes behavior, leave it alone and flag it.

## 1. Early Returns (Guard Clauses)

Invert conditionals to exit early. Reduces nesting and makes the happy path obvious.

**PHP — Before:**
```php
public function processOrder(Order $order): void
{
    if ($order->isPending()) {
        if ($order->hasStock()) {
            if ($order->user->isActive()) {
                $this->charge($order);
                $this->ship($order);
                $this->notify($order);
            }
        }
    }
}
```

**PHP — After:**
```php
public function processOrder(Order $order): void
{
    if (! $order->isPending()) return;
    if (! $order->hasStock()) return;
    if (! $order->user->isActive()) return;

    $this->charge($order);
    $this->ship($order);
    $this->notify($order);
}
```

**TypeScript — Before:**
```typescript
function getDiscount(user: User): number {
    if (user.isActive) {
        if (user.isPremium) {
            if (user.yearsActive > 5) {
                return 0.30;
            } else {
                return 0.20;
            }
        } else {
            return 0.10;
        }
    } else {
        return 0;
    }
}
```

**TypeScript — After:**
```typescript
function getDiscount(user: User): number {
    if (!user.isActive) return 0;
    if (!user.isPremium) return 0.10;
    return user.yearsActive > 5 ? 0.30 : 0.20;
}
```

## 2. Promise Chains to Async/Await

Flattens callback pyramids and makes error handling explicit.

**Before:**
```typescript
function loadUserDashboard(userId: string) {
    return fetchUser(userId)
        .then(user => {
            return fetchOrders(user.id)
                .then(orders => {
                    return fetchStats(user.id)
                        .then(stats => ({ user, orders, stats }));
                });
        })
        .catch(err => {
            console.error(err);
            return null;
        });
}
```

**After:**
```typescript
async function loadUserDashboard(userId: string) {
    try {
        const user = await fetchUser(userId);
        const [orders, stats] = await Promise.all([
            fetchOrders(user.id),
            fetchStats(user.id),
        ]);
        return { user, orders, stats };
    } catch (err) {
        logger.error('Dashboard load failed', { userId, err });
        return null;
    }
}
```

Note: `Promise.all` only when calls are independent (no data dependency between them).

## 3. Extract Nested Logic into Named Functions

A named function at the call site documents intent.

**PHP — Before:**
```php
public function applyDiscount(Cart $cart): float
{
    $total = $cart->total;
    if ($cart->user->created_at < now()->subYear()
        && $cart->user->orders()->count() > 5
        && $cart->total > 100) {
        $total = $cart->total * 0.85;
    }
    return $total;
}
```

**PHP — After:**
```php
public function applyDiscount(Cart $cart): float
{
    if ($this->qualifiesForLoyaltyDiscount($cart)) {
        return $cart->total * 0.85;
    }
    return $cart->total;
}

private function qualifiesForLoyaltyDiscount(Cart $cart): bool
{
    return $cart->user->created_at < now()->subYear()
        && $cart->user->orders()->count() > 5
        && $cart->total > 100;
}
```

## 4. Eliminate Redundant State

Derived values should be computed, not stored and kept in sync.

**TypeScript — Before:**
```typescript
const [items, setItems] = useState<Item[]>([]);
const [itemCount, setItemCount] = useState(0);
const [isEmpty, setIsEmpty] = useState(true);

function addItem(item: Item) {
    const newItems = [...items, item];
    setItems(newItems);
    setItemCount(newItems.length);
    setIsEmpty(newItems.length === 0);
}
```

**TypeScript — After:**
```typescript
const [items, setItems] = useState<Item[]>([]);
const itemCount = items.length;         // derived
const isEmpty = items.length === 0;     // derived

function addItem(item: Item) {
    setItems(prev => [...prev, item]);
}
```

## 5. Simplify Boolean Expressions

Remove double-negatives, redundant comparisons, and verbosity.

**Before:**
```php
if ($user->status !== 'inactive' && $user->status !== 'banned') { /* allowed */ }
if ($isAdmin === true) { ... }
return $count > 0 ? true : false;
```

**After:**
```php
if (in_array($user->status, ['active', 'pending'])) { /* allowed */ }
if ($isAdmin) { ... }
return $count > 0;
```

## 6. Flatten Collection Pipelines

Prefer expressive collection methods over manual loops.

**Before:**
```php
$result = [];
foreach ($orders as $order) {
    if ($order->status === 'completed') {
        $result[] = $order->total;
    }
}
$sum = array_sum($result);
```

**After:**
```php
$sum = collect($orders)
    ->where('status', 'completed')
    ->sum('total');
```

## Identification Checklist

For each function/component, check:
- [ ] Nesting depth > 3? -> Early returns candidate
- [ ] `.then().then()` chains? -> Async/await candidate
- [ ] Inline condition > 3 clauses? -> Extract to named function
- [ ] Multiple state values derivable from one? -> Eliminate redundant state
- [ ] `=== true`, `!== false`, ternary returning bool? -> Boolean cleanup
- [ ] Manual loop with filter + map? -> Collection pipeline

## Rules

- One logical change per edit — don't mix early returns with extract-function in one diff
- Preserve all comments that explain *why* (not *what*)
- Keep variable names — don't rename as part of simplification
- Don't change function signatures (parameter names, types, return types)
