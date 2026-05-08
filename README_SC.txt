Módulo Main@SC integrado ao Magi@Balthazar

1) WEB_INTERFACE
- Abra merged/web_interface/index.html
- Navegue em Main@SC no menu lateral

2) TABELA NO SUPABASE
create table if not exists public.purchase_requests (
  id uuid primary key default gen_random_uuid(),
  sc_number text not null,
  cc text not null,
  observation text not null,
  status text not null default 'PENDENTE',
  contingencia boolean not null default false,
  valor_total numeric not null default 0,
  created_at timestamp with time zone not null default now()
);

3) STREAMLIT
pip install -r requirements_streamlit.txt
Crie .streamlit/secrets.toml com:
SUPABASE_URL="..."
SUPABASE_KEY="..."
Rode:
streamlit run streamlit_magi_sc.py
