# Stack: Perl

**Versiones:** Perl 5.36+ · Mojolicious · PostgreSQL · Test2 · Ruff · cpanm

## Inicializar

```bash
make dev-stack STACK=perl
```

Activa: reglas Perl, slash commands, CLAUDE.md con plantilla.

---

## Slash commands activados

| Comando | Cuándo usarlo |
| --- | --- |
| `/jedi-review` | Para código crítico (3 expertos: Beck, Fowler, Acton) |
| `/git-workflow` | Workflow de commits y PRs |
| `/workflow-runner <nombre>` | Ejecutar pipelines (`feature`, `hotfix`, `refactor`) |
| `/canary-watch URL` | Monitoreo post-deploy en staging/producción |
| `/security-scan` | Auditoría de seguridad de configuración y `.claude/` |
| `/benchmark` | Medir regresiones de rendimiento en endpoints |
| `/codebase-onboarding` | Generar guía de onboarding del repo |

Las prácticas `perl-patterns`, `moose-oop`, `async-handling`, `testing-test2` y `database-integration` se aplican como skills embebidas en los agentes del stack.

---

## Convenciones clave

### Arquitectura — MVC con Mojolicious

```text
lib/
├── MyApp.pm               ← @Mojolicious::Lite app entrypoint
├── MyApp/
│   ├── Controller/        ← Controladores Mojolicious
│   │   ├── Users.pm
│   │   └── Auth.pm
│   ├── Model/             ← Lógica de negocio
│   │   ├── User.pm
│   │   └── Session.pm
│   ├── DB/                ← Acceso a datos
│   │   ├── User.pm
│   │   └── Transaction.pm
│   └── Util/              ← Helpers
│       ├── Validator.pm
│       └── Email.pm
t/
├── controllers/           ← Tests de controladores
├── models/                ← Tests de modelos
└── integration/           ← Tests de integración
```

### Controllers — Delegación clara

```perl
# CORRECTO: controlador delgado delegando a model
package MyApp::Controller::Users;
use Mojo::Base 'Mojolicious::Controller';

sub list {
    my $self = shift;
    
    my $page = $self->param('page') // 1;
    my $limit = $self->param('limit') // 20;
    
    my $users = MyApp::Model::User->list(
        page  => $page,
        limit => $limit
    );
    
    $self->render(json => {
        success => 1,
        data    => $users->{data},
        meta    => {
            page  => $page,
            limit => $limit,
            total => $users->{total}
        }
    });
}

sub create {
    my $self = shift;
    
    my $name  = $self->param('name');
    my $email = $self->param('email');
    
    # Validación
    return $self->render(
        status => 400,
        json   => { error => 'Name required' }
    ) unless $name;
    
    return $self->render(
        status => 400,
        json   => { error => 'Invalid email' }
    ) unless $email =~ /\@/;
    
    my $user = MyApp::Model::User->create(
        name  => $name,
        email => $email
    );
    
    $self->render(
        status => 201,
        json   => { success => 1, data => $user }
    );
}

# INCORRECTO: lógica de negocio en el controlador
sub bad_create {
    my $self = shift;
    
    my $dbh = DBI->connect('dbi:Pg:...');  # ← Conexión directa
    my $email = $self->param('email');
    
    $dbh->do('INSERT INTO users (email) VALUES (?)', undef, $email);  # ← Sin validación
    $self->render(json => { ok => 1 });
}
```

### Model — Lógica de negocio centralizada

```perl
# CORRECTO: modelo con validación y lógica
package MyApp::Model::User;
use Mojo::Base -base;
use Mojo::Util 'dumper';

has 'db';

sub list {
    my ($self, %opts) = @_;
    
    my $page  = $opts{page} // 1;
    my $limit = $opts{limit} // 20;
    my $offset = ($page - 1) * $limit;
    
    my $users = $self->db->query(
        'SELECT * FROM users LIMIT ? OFFSET ?',
        $limit, $offset
    )->hashes->to_array;
    
    my $total = $self->db->query('SELECT COUNT(*) FROM users')
        ->hash->{count};
    
    return {
        data  => $users,
        total => $total
    };
}

sub create {
    my ($self, %opts) = @_;
    
    # Validación de reglas de negocio
    die 'Email already exists'
        if $self->db->query('SELECT 1 FROM users WHERE email = ?', $opts{email})
            ->hash;
    
    my $user = $self->db->query(
        'INSERT INTO users (name, email) VALUES (?, ?) RETURNING *',
        $opts{name}, $opts{email}
    )->hash;
    
    return $user;
}
```

### Database — DBIx con prepared statements

```perl
# CORRECTO: prepared statements y transacciones
package MyApp::DB;
use Mojo::Base -base;
use DBI;

has 'dbh';

sub new {
    my $class = shift;
    my $dbh = DBI->connect(
        'dbi:Pg:dbname=myapp;host=localhost',
        'postgres',
        '',
        { RaiseError => 1, AutoCommit => 0 }
    );
    return $class->SUPER::new(dbh => $dbh);
}

sub create_user_with_role {
    my ($self, $name, $email, $role) = @_;
    
    eval {
        my $user_sth = $self->dbh->prepare(
            'INSERT INTO users (name, email) VALUES (?, ?) RETURNING id'
        );
        $user_sth->execute($name, $email);
        my ($user_id) = $user_sth->fetchrow;
        
        my $role_sth = $self->dbh->prepare(
            'INSERT INTO user_roles (user_id, role) VALUES (?, ?)'
        );
        $role_sth->execute($user_id, $role);
        
        $self->dbh->commit;
    };
    
    if ($@) {
        $self->dbh->rollback;
        die "Failed to create user: $@";
    }
    
    return 1;
}

# INCORRECTO: sin prepared statements (SQL injection)
sub bad_query {
    my ($self, $email) = @_;
    my $sth = $self->dbh->prepare("SELECT * FROM users WHERE email = '$email'");  # ← SQL injection!
    $sth->execute;
    return $sth->fetchall_arrayref({});
}
```

### Routes — Mojolicious::Lite

```perl
# CORRECTO: rutas con validación y middleware
package MyApp;
use Mojolicious::Lite -signatures;

# Middleware de autenticación
under sub {
    my $c = shift;
    
    return 1 if $c->session('user_id');
    $c->render(status => 401, json => { error => 'Unauthorized' });
    return undef;
};

# GET /api/users?page=1&limit=20
get '/api/users' => sub ($c) {
    my $page = $c->param('page') // 1;
    my $limit = $c->param('limit') // 20;
    
    # Validación de límites
    $limit = 100 if $limit > 100;
    
    my $users = MyApp::Model::User->list(
        page  => $page,
        limit => $limit
    );
    
    $c->render(json => {
        success => 1,
        data    => $users->{data},
        meta    => { page => $page, limit => $limit, total => $users->{total} }
    });
};

# POST /api/users
post '/api/users' => sub ($c) {
    my $name  = $c->param('name');
    my $email = $c->param('email');
    
    # Validación
    return $c->render(
        status => 400,
        json   => { error => 'Name required' }
    ) unless $name && $name =~ /\S/;
    
    return $c->render(
        status => 400,
        json   => { error => 'Invalid email' }
    ) unless $email && $email =~ /\@/;
    
    my $user = MyApp::Model::User->create(
        name  => $name,
        email => $email
    );
    
    $c->render(
        status => 201,
        json   => { success => 1, data => $user }
    );
};

app->start;

# INCORRECTO: sin validación, sin middleware
get '/bad' => sub ($c) {
    my $id = $c->param('id');
    my $users = $c->db->query("SELECT * FROM users WHERE id = $id")->hashes;  # ← Sin validación
    $c->render(json => $users);
};
```

### Testing — Test2

```perl
# CORRECT: test with Test2
use Test2::V0;
use MyApp::Model::User;
use Test::MockObject;

sub test_user_list {
    my $db = Test::MockObject->new;
    $db->mock('query', sub {
        my ($self, $sql, @args) = @_;
        return Test::MockObject->new
            ->mock('hashes', sub {
                return Test::MockObject->new
                    ->mock('to_array', sub {
                        return [
                            { id => 1, name => 'Alice', email => 'alice@example.com' },
                            { id => 2, name => 'Bob', email => 'bob@example.com' }
                        ];
                    });
            });
    });
    
    my $model = MyApp::Model::User->new(db => $db);
    my $result = $model->list(page => 1, limit => 20);
    
    is($result->{data}, array {
        item { hash { field 'name' => 'Alice'; } };
        item { hash { field 'name' => 'Bob'; } };
        end;
    }, 'List returns users');
    
    ok($result->{total} > 0, 'Total count present');
}

done_testing;

# INCORRECTO: test sin mocks, hablando a base de datos real
use Test::More;

my $dbh = DBI->connect('dbi:Pg:dbname=test_db');
my $sth = $dbh->prepare('SELECT * FROM users LIMIT 2');  # ← Depende de estado externo
$sth->execute;
my $users = $sth->fetchall_arrayref({});

is(scalar @$users, 2, 'Got two users');  # ← Test frágil
```

---

## Anti-patrones a evitar

- **Lógica de negocio en controladores** — mover a Model
- **Queries SQL inline sin prepared statements** — riesgo de SQL injection
- **Sin validación en los parámetros de entrada** — siempre validar antes de procesar
- **Transacciones sin rollback en caso de error** — usar eval/die para garantizar rollback
- **Mágicos global state con package variables** — usar objetos con Mojo::Base
- **Tests sin mocks** — tests acoplados a base de datos real, lentos y frágiles
- **Sin manejo de excepciones en Model** — siempre capturar y loguear errores
- **DBIx sin statement handles reutilizables** — preparar statements una vez, ejecutar muchas
- **Rutas sin límites de paginación** — siempre limitar LIMIT máximo

---

## Comandos útiles

```bash
# Desarrollo
perl -Ilib script/myapp daemon

# Tests
perl -Ilib -MTest2::V0 t/test.t
prove -l t/

# Instalación de módulos
cpanm Module::Name
cpanm --installdeps .

# Linting
perlcritic lib/

# Base de datos
psql -d myapp_db
```

## Variables de entorno

```bash
PERL_ENV=development
DATABASE_URL=postgresql://postgres:@localhost:5432/myapp_db
DATABASE_POOL_SIZE=10

MOJOLICIOUS_MODE=development
LOG_LEVEL=debug

JWT_SECRET=super-secret-key-change-in-production
SESSION_TIMEOUT=3600

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=app-password
```

---

## Ejemplo completo

→ [CLAUDE.md para Perl Mojolicious](/examples/perl-mojolicious-CLAUDE)
